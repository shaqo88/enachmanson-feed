#!/usr/bin/env python3
"""
recover_from_r2.py — Read-only inventory of what's actually in the R2 bucket,
reconciled against yt/episodes.json.

Run this BEFORE re-running sync_episodes.py whenever episodes.json looks
suspicious (empty, partial, or out of sync) — it tells you exactly what's
sitting in R2 already so you don't lose track of already-uploaded files or
re-download audio that's already there.

Modes:
  (default)   Report only. Prints the diff between R2 and episodes.json. No writes.
  --rebuild   Reconstruct episodes.json entries for any R2 file that's missing
              from episodes.json, by re-fetching metadata (title/description/
              duration/publish date) from YouTube via yt-dlp — metadata only,
              no re-download of audio. feed.xml is NOT regenerated; run
              build_feeds.py afterward to rebuild the feed.

Destination path in repo: yt/recover_from_r2.py
"""

import os
import json
import argparse
import sys
from pathlib import Path

import boto3
import yt_dlp

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

R2_ACCOUNT_ID = os.environ["R2_ACCOUNT_ID"]
R2_ACCESS_KEY = os.environ["R2_ACCESS_KEY"]
R2_SECRET_KEY = os.environ["R2_SECRET_KEY"]
R2_BUCKET     = os.environ["R2_BUCKET"]
R2_PUBLIC_URL = os.environ["R2_PUBLIC_URL"].rstrip("/")

EPISODES_FILE = Path("yt/episodes.json")
COOKIES_FILE  = Path("/tmp/yt_cookies.txt")  # optional — used only if present


def list_r2_mp3s(s3) -> dict:
    """Return {video_id: {'key': ..., 'size': ...}} for every .mp3 in the bucket."""
    found = {}
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=R2_BUCKET):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".mp3"):
                vid_id = key[:-4]
                found[vid_id] = {"key": key, "size": obj["Size"]}
    return found


def fetch_metadata(vid_id: str) -> dict:
    opts = {
        "quiet": True,
        "skip_download": True,
        "extractor_args": {"youtube": {"player_client": ["tv", "web"]}},
    }
    if COOKIES_FILE.exists():
        opts["cookiefile"] = str(COOKIES_FILE)
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(f"https://www.youtube.com/watch?v={vid_id}", download=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rebuild", action="store_true",
        help="Write missing entries back into episodes.json (default is report-only)",
    )
    args = parser.parse_args()

    known = json.loads(EPISODES_FILE.read_text(encoding="utf-8")) if EPISODES_FILE.exists() else {}
    print(f"📚 episodes.json currently has {len(known)} entries")

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
    )

    in_r2 = list_r2_mp3s(s3)
    print(f"☁️  R2 bucket has {len(in_r2)} .mp3 file(s)")

    missing_from_json = sorted(set(in_r2) - set(known))
    available_known = {
        vid_id for vid_id, episode in known.items()
        if not episode.get("unavailable")
    }
    unavailable_known = {
        vid_id for vid_id, episode in known.items()
        if episode.get("unavailable")
    }
    orphaned_in_json = sorted(available_known - set(in_r2))

    print(f"\n🔍 In R2 but NOT in episodes.json: {len(missing_from_json)}")
    for vid in missing_from_json:
        size_mb = in_r2[vid]["size"] / 1024 / 1024
        print(f"   {vid}  ({size_mb:.1f} MB)")

    print(f"\n🔍 In episodes.json but NOT in R2 (would 404 in the feed): {len(orphaned_in_json)}")
    for vid in orphaned_in_json:
        print(f"   {vid}  — {known[vid].get('title', '?')}")
    print(f"\nℹ️  Unavailable entries intentionally excluded from the feed: {len(unavailable_known)}")

    if not args.rebuild:
        print("\nℹ️  Read-only report only. Re-run with --rebuild to patch episodes.json.")
        return

    if not missing_from_json:
        print("\n✅ Nothing to rebuild.")
        return

    print(f"\n🔧 Rebuilding {len(missing_from_json)} missing entr(ies)...")
    for vid_id in missing_from_json:
        try:
            meta = fetch_metadata(vid_id)
        except Exception as e:
            print(f"   ❌ Could not fetch metadata for {vid_id}: {e}")
            continue
        info = in_r2[vid_id]
        known[vid_id] = {
            "id": vid_id,
            "title": meta.get("title", vid_id),
            "description": meta.get("description", "") or meta.get("title", vid_id),
            "published": meta.get("upload_date", ""),
            "duration": meta.get("duration", 0),
            "url": f"{R2_PUBLIC_URL}/{info['key']}",
            "size": info["size"],
        }
        print(f"   ✅ Recovered {vid_id} — {meta.get('title', '?')}")

    EPISODES_FILE.write_text(json.dumps(known, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 Wrote {len(known)} total entries to {EPISODES_FILE}")
    print("ℹ️  Feeds were not regenerated. Run yt/build_feeds.py next.")


if __name__ == "__main__":
    main()
