#!/usr/bin/env python3
"""
sync_podcast.py — YouTube playlist → MP3 on Cloudflare R2 → RSS feed on GitHub Pages

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
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from pathlib import Path

# ── Config from environment ────────────────────────────────────────────────────
PLAYLIST_ID   = os.environ["PLAYLIST_ID"]
R2_ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
R2_ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY = os.environ["R2_SECRET_KEY"]
R2_BUCKET     = os.environ["R2_BUCKET"]
R2_PUBLIC_URL = os.environ["R2_PUBLIC_URL"].rstrip("/")

COOKIES_FILE  = Path("/tmp/yt_cookies.txt")

EPISODES_FILE = Path("yt/episodes.json")
FEED_FILE     = Path("feed.xml")
FEED_URL      = "https://shaqo88.github.io/enachmanson-feed/feed.xml"
PODCAST_TITLE = "שיעורי הרב אלחנן נחמנסון"
PODCAST_DESC  = "שיעורי הלכה, חסידות וחינוך מאת הרב אלחנן נחמנסון"
AUTHOR_NAME   = "הרב אלחנן נחמנסון"
LOGO_URL      = f"{R2_PUBLIC_URL}/logo.png"

# How many recent playlist items to check each run (saves time; raise if needed)
PLAYLIST_FETCH_COUNT = 50

# ── Cookie options (added to every yt-dlp call) ───────────────────────────────
def cookie_opts() -> dict:
    if COOKIES_FILE.exists():
        return {"cookiefile": str(COOKIES_FILE)}
    return {}

# ── Load known episodes ────────────────────────────────────────────────────────
if EPISODES_FILE.exists():
    known: dict = json.loads(EPISODES_FILE.read_text(encoding="utf-8"))
else:
    known = {}

print(f"📚 Loaded {len(known)} known episodes")

# ── Fetch YouTube playlist metadata (no download) ──────────────────────────────
ydl_info_opts = {
    "quiet": True,
    "extract_flat": True,
    "playlistend": PLAYLIST_FETCH_COUNT,
    **cookie_opts(),
}

with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
    playlist_info = ydl.extract_info(
        f"https://www.youtube.com/playlist?list={PLAYLIST_ID}",
        download=False,
    )

entries = playlist_info.get("entries", [])
print(f"📋 Playlist has {len(entries)} entries (checked last {PLAYLIST_FETCH_COUNT})")

# ── S3-compatible client for Cloudflare R2 ────────────────────────────────────
s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    region_name="auto",
)

# ── Process new episodes ───────────────────────────────────────────────────────
new_count = 0

for entry in entries:
    vid_id = entry.get("id")
    if not vid_id:
        continue

    if vid_id in known:
        continue  # already processed

    title = entry.get("title", f"Episode {vid_id}")
    print(f"\n🆕 New video: {title} ({vid_id})")

    # Download audio to /tmp
    tmp_mp3 = Path(f"/tmp/{vid_id}.mp3")
    ydl_dl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"/tmp/{vid_id}.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": False,
        **cookie_opts(),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_dl_opts) as ydl:
            meta = ydl.extract_info(f"https://www.youtube.com/watch?v={vid_id}", download=True)
    except Exception as e:
        print(f"  ❌ Download failed for {vid_id}: {e}")
        continue  # skip this episode; next run will retry

    if not tmp_mp3.exists():
        print(f"  ❌ Expected {tmp_mp3} not found after download; skipping")
        continue

    file_size = tmp_mp3.stat().st_size
    r2_key    = f"{vid_id}.mp3"

    # Upload to R2
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

    # Clean up local file
    tmp_mp3.unlink(missing_ok=True)

    # Only now record the episode as known
    upload_date = meta.get("upload_date", "")  # YYYYMMDD
    ep = {
        "id":          vid_id,
        "title":       meta.get("title", title),
        "description": meta.get("description", "") or title,
        "published":   upload_date,
        "duration":    meta.get("duration", 0),
        "url":         f"{R2_PUBLIC_URL}/{r2_key}",
        "size":        file_size,
    }
    known[vid_id] = ep
    new_count += 1

    # Save after each successful episode (so a crash mid-run doesn't lose work)
    EPISODES_FILE.write_text(
        json.dumps(known, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  💾 Saved to episodes.json")

print(f"\n📥 Processed {new_count} new episode(s)")

# ── Generate RSS feed ──────────────────────────────────────────────────────────
fg = FeedGenerator()
fg.load_extension("podcast")

fg.id(FEED_URL)
fg.title(PODCAST_TITLE)
fg.description(PODCAST_DESC)
fg.author({"name": AUTHOR_NAME})
fg.link(href=FEED_URL, rel="self")
fg.language("he")
fg.image(LOGO_URL)
fg.podcast.itunes_category("Religion & Spirituality", "Judaism")
fg.podcast.itunes_explicit("no")
fg.podcast.itunes_author(AUTHOR_NAME)
fg.podcast.itunes_image(LOGO_URL)

def parse_date(yyyymmdd: str) -> datetime:
    try:
        return datetime.strptime(yyyymmdd, "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime(2000, 1, 1, tzinfo=timezone.utc)

episodes_sorted = sorted(known.values(), key=lambda x: x["published"], reverse=True)

for ep in episodes_sorted:
    fe = fg.add_entry()
    fe.id(f"yt:video:{ep['id']}")          # matches existing PodBean GUIDs exactly
    fe.title(ep["title"])
    fe.description(ep["description"] or ep["title"])
    fe.published(parse_date(ep["published"]))
    fe.updated(parse_date(ep["published"]))
    fe.enclosure(ep["url"], str(ep["size"]), "audio/mpeg")
    fe.podcast.itunes_duration(ep["duration"])
    fe.podcast.itunes_explicit("no")

fg.rss_file(str(FEED_FILE), pretty=True)
print(f"✅ feed.xml written with {len(episodes_sorted)} episodes")
