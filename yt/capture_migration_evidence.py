#!/usr/bin/env python3
"""Capture public migration evidence into a timestamped artifact directory."""

import argparse
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

import requests
from PIL import Image

PODBEAN_FEED_URL = "https://feed.podbean.com/enachmanson/feed.xml"
CANONICAL_FEED_URL = "https://shaqo88.github.io/enachmanson-feed/feed.xml"
ARTWORK_URL = "https://shaqo88.github.io/enachmanson-feed/assets/podcast-cover.png"
APPLE_SEARCH_URL = "https://itunes.apple.com/search"
SHOW_TITLE = "שיעורי הרב אלחנן נחמנסון"
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
TIMEOUT = 45

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def fetch(session: requests.Session, url: str) -> requests.Response:
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response


def parse_feed(data: bytes) -> dict:
    root = ET.fromstring(data)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("RSS feed has no channel")
    items = channel.findall("item")
    guids = [(item.findtext("guid") or "").strip() for item in items]
    return {
        "title": (channel.findtext("title") or "").strip(),
        "items": len(items),
        "guids": guids,
        "unique_guids": len(set(guids)),
        "new_feed_url": (
            channel.findtext(f"{{{ITUNES_NS}}}new-feed-url") or ""
        ).strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = "enachmanson-feed-migration-evidence"

    try:
        podbean = fetch(session, PODBEAN_FEED_URL)
        canonical = fetch(session, CANONICAL_FEED_URL)
        artwork = fetch(session, ARTWORK_URL)

        podbean_path = output_dir / "podbean-feed.xml"
        canonical_path = output_dir / "canonical-feed.xml"
        artwork_path = output_dir / "podcast-cover.png"
        podbean_path.write_bytes(podbean.content)
        canonical_path.write_bytes(canonical.content)
        artwork_path.write_bytes(artwork.content)

        podbean_data = parse_feed(podbean.content)
        canonical_data = parse_feed(canonical.content)
        with Image.open(io.BytesIO(artwork.content)) as image:
            artwork_dimensions = list(image.size)

        apple = session.get(
            APPLE_SEARCH_URL,
            params={
                "term": SHOW_TITLE,
                "entity": "podcast",
                "country": "il",
                "limit": 50,
            },
            timeout=TIMEOUT,
        )
        apple.raise_for_status()
        apple_results = apple.json()
        (output_dir / "apple-directory-search.json").write_text(
            json.dumps(apple_results, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        podbean_guids = set(podbean_data.pop("guids"))
        canonical_guids = set(canonical_data.pop("guids"))
        report = {
            "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "sources": {
                "podbean_feed": PODBEAN_FEED_URL,
                "canonical_feed": CANONICAL_FEED_URL,
                "artwork": ARTWORK_URL,
            },
            "podbean": podbean_data,
            "canonical": canonical_data,
            "guid_sets_match": podbean_guids == canonical_guids,
            "podbean_only_guids": sorted(podbean_guids - canonical_guids),
            "canonical_only_guids": sorted(canonical_guids - podbean_guids),
            "artwork_dimensions": artwork_dimensions,
            "apple_results": [
                {
                    "collection_name": result.get("collectionName"),
                    "artist_name": result.get("artistName"),
                    "listing_url": result.get("collectionViewUrl"),
                    "feed_url": result.get("feedUrl"),
                    "track_id": result.get("trackId"),
                }
                for result in apple_results.get("results", [])
            ],
        }
        (output_dir / "evidence-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, ET.ParseError, requests.RequestException) as exc:
        print(f"❌ Evidence capture failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["guid_sets_match"]:
        print("❌ Podbean and canonical GUID sets differ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
