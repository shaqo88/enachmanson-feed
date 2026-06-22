#!/usr/bin/env python3
"""
sync_episodes.py — YouTube playlist → MP3 on Cloudflare R2 → episodes.json

Pulls new videos from the YouTube playlist, converts them to 64kbps MP3,
uploads to Cloudflare R2, and records each one in yt/episodes.json.

This script has NO knowledge of feed formats — that's build_feeds.py's job.
Run build_feeds.py after this to regenerate feed.xml / feed-standard.xml.

Recovery guarantee:
  Episodes are only written to episodes.json AFTER a successful R2 upload.
  If the script fails mid-run, the next run will retry the missing episodes.
  Running this script multiple times is safe (idempotent).
"""

import os
import json
import yt_dlp
import boto3
from botocore.exceptions import ClientError
from pathlib import Path

# ── Config from environment ────────────────────────────────────────────────
PLAYLIST_ID   = os.environ["PLAYLIST_ID"]
R2_ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
R2_ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY = os.environ["R2_SECRET_KEY"]
R2_BUCKET     = os.environ["R2_BUCKET"]
R2_PUBLIC_URL = os.environ["R2_PUBLIC_URL"].rstrip("/")

COOKIES_FILE  = Path("/tmp/yt_cookies.txt")  # optional — used only if present
EPISODES_FILE = Path("yt/episodes.json")

# How many recent playlist items to check each run
PLAYLIST_FETCH_COUNT = 150


def common_opts() -> dict:
    opts = {
        "extractor_args": {"youtube": {"player_client": ["tv", "web"]}},
    }
    if COOKIES_FILE.exists():
        opts["cookiefile"] = str(COOKIES_FILE)
    return opts


def main():
    # ── Load known episodes ──────────────────────────────────────────────────
    known = json.loads(EPISODES_FILE.read_text(encoding="utf-8")) if EPISODES_FILE.exists() else {}
    print(f"📚 Loaded {len(known)} known episodes")

    # ── Fetch YouTube playlist metadata (no download) ───────────────────────
    ydl_info_opts = {
        "quiet": True,
        "extract_flat": True,
        "playlistend": PLAYLIST_FETCH_COUNT,
        **common_opts(),
    }
    with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
        playlist_info = ydl.extract_info(
            f"https://www.youtube.com/playlist?list={PLAYLIST_ID}",
            download=False,
        )
    entries = playlist_info.get("entries", [])
    print(f"📋 Playlist has {len(entries)} entries (checked last {PLAYLIST_FETCH_COUNT})")

    # ── S3-compatible client for Cloudflare R2 ───────────────────────────────
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
    )

    # ── Process new episodes ─────────────────────────────────────────────────
    new_count = 0
    for entry in entries:
        vid_id = entry.get("id")
        if not vid_id:
            continue
        if vid_id in known:
            continue  # already processed

        title = entry.get("title", f"Episode {vid_id}")
        print(f"\n🆕 New video: {title} ({vid_id})")

        tmp_mp3 = Path(f"/tmp/{vid_id}.mp3")
        ydl_dl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"/tmp/{vid_id}.%(ext)s",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "64",   # 64kbps — voice quality, half the size of 128kbps
            }],
            "quiet": False,
            **common_opts(),
        }

        PERMANENT_UNAVAILABLE_MARKERS = (
            "video unavailable",
            "private video",
            "video is private",
            "removed by the uploader",
            "terminated",
            "removed for violating",
        )

        try:
            with yt_dlp.YoutubeDL(ydl_dl_opts) as ydl:
                meta = ydl.extract_info(f"https://www.youtube.com/watch?v={vid_id}", download=True)
        except Exception as e:
            err_str = str(e).lower()
            if any(marker in err_str for marker in PERMANENT_UNAVAILABLE_MARKERS):
                print(f"  ⚠️  Permanently unavailable, will not retry: {vid_id} — {e}")
                known[vid_id] = {"id": vid_id, "title": title, "unavailable": True}
                EPISODES_FILE.write_text(
                    json.dumps(known, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            else:
                print(f"  ❌ Download failed for {vid_id}: {e}")
            continue  # only retried next run if NOT marked unavailable
          
        if not tmp_mp3.exists():
            print(f"  ❌ Expected {tmp_mp3} not found after download; skipping")
            continue

        file_size = tmp_mp3.stat().st_size
        r2_key    = f"{vid_id}.mp3"

        try:
            s3.upload_file(
                str(tmp_mp3),
                R2_BUCKET,
                r2_key,
                ExtraArgs={"ContentType": "audio/mpeg"},
            )
            print(f"  ✅ Uploaded to R2: {r2_key} ({file_size // 1024 // 1024} MB)")
        except ClientError as e:
            print(f"  ❌ R2 upload failed for {vid_id}: {e}")
            tmp_mp3.unlink(missing_ok=True)
            continue  # skip; next run will retry

        tmp_mp3.unlink(missing_ok=True)

        upload_date = meta.get("upload_date", "")  # YYYYMMDD
        known[vid_id] = {
            "id":          vid_id,
            "title":       meta.get("title", title),
            "description": meta.get("description", "") or title,
            "published":   upload_date,
            "duration":    meta.get("duration", 0),
            "url":         f"{R2_PUBLIC_URL}/{r2_key}",
            "size":        file_size,
        }
        new_count += 1

        # Save after each episode — crash-safe
        EPISODES_FILE.write_text(
            json.dumps(known, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  💾 Saved to episodes.json")

    print(f"\n📥 Processed {new_count} new episode(s)")


if __name__ == "__main__":
    main()
