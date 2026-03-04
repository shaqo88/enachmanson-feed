#!/usr/bin/env python3
"""
Feed Change Detector
Fetches the Podbean RSS feed, computes a hash, and compares it against the
last known hash. Outputs changed=true/false for use in GitHub Actions.
Usage: python3 check_feed.py
"""

import hashlib
import os
import sys
import urllib.request
import urllib.error

PODBEAN_FEED_URL = "https://feed.podbean.com/enachmanson/feed.xml"
HASH_FILE        = "last_hash.txt"


def fetch_feed(url: str) -> str:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP error fetching feed: {e.code} {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ Network error fetching feed: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error fetching feed: {e}")
        sys.exit(1)


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_output(key: str, value: str):
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")


def main():
    print(f"Fetching {PODBEAN_FEED_URL} ...")
    raw = fetch_feed(PODBEAN_FEED_URL)
    new_hash = compute_hash(raw)

    old_hash = ""
    if os.path.exists(HASH_FILE):
        old_hash = open(HASH_FILE).read().strip()

    if new_hash == old_hash:
        print("✅ Feed unchanged — skipping update job.")
        write_output("changed", "false")
    else:
        print("🆕 Feed has changed — will run update job.")
        write_output("changed", "true")


if __name__ == "__main__":
    main()
