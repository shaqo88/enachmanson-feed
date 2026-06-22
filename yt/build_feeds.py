#!/usr/bin/env python3
"""
build_feeds.py — episodes.json → RSS feeds (no network calls, no R2, no YouTube)

Reads the shared episode database and writes two feeds from the exact same data:

  feed.xml           Zinc-compatible feed. Name and URL are frozen — Zinc already
                      depends on this exact path. Includes the spotify: namespace
                      fields Zinc requires (ported from the old convert_feed.py).

  feed-standard.xml  Clean, namespace-free feed intended for Spotify for
                      Podcasters / Apple Podcasts Connect submission.

Safe to re-run any time episodes.json changes, or whenever feed formatting needs
a fix — never touches YouTube or R2.
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from feedgen.feed import FeedGenerator

# ── Config ────────────────────────────────────────────────────────────────────
EPISODES_FILE       = Path("yt/episodes.json")
FEED_ZINC_FILE      = Path("feed.xml")            # frozen name/URL — Zinc depends on this
FEED_STANDARD_FILE  = Path("feed-standard.xml")   # new — for Spotify/Apple submission

FEED_URL_ZINC       = "https://shaqo88.github.io/enachmanson-feed/feed.xml"
FEED_URL_STANDARD   = "https://shaqo88.github.io/enachmanson-feed/feed-standard.xml"

PODCAST_TITLE = "שיעורי הרב אלחנן נחמנסון"
PODCAST_DESC  = "שיעורי הלכה, חסידות וחינוך מאת הרב אלחנן נחמנסון"
AUTHOR_NAME   = "הרב אלחנן נחמנסון"

R2_PUBLIC_URL = os.environ.get("R2_PUBLIC_URL", "").rstrip("/")
LOGO_URL      = f"{R2_PUBLIC_URL}/logo.png" if R2_PUBLIC_URL else ""

SPOTIFY_NS    = "http://www.spotify.com/ns/rss"
SPOTIFY_LIMIT = 100


def parse_date(yyyymmdd: str) -> datetime:
    try:
        return datetime.strptime(yyyymmdd, "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime(2000, 1, 1, tzinfo=timezone.utc)


def build_base_feed(feed_url: str) -> FeedGenerator:
    fg = FeedGenerator()
    fg.load_extension("podcast")
    fg.id(feed_url)
    fg.title(PODCAST_TITLE)
    fg.description(PODCAST_DESC)
    fg.author({"name": AUTHOR_NAME})
    fg.link(href=feed_url, rel="self")
    fg.language("he")
    if LOGO_URL:
        fg.image(LOGO_URL)
    fg.podcast.itunes_category("Religion & Spirituality", "Judaism")
    fg.podcast.itunes_explicit("no")
    fg.podcast.itunes_author(AUTHOR_NAME)
    if LOGO_URL:
        fg.podcast.itunes_image(LOGO_URL)
    return fg


def add_episodes(fg: FeedGenerator, episodes_sorted: list) -> None:
    for ep in episodes_sorted:
        fe = fg.add_entry()
        fe.id(f"yt:video:{ep['id']}")   # matches existing PodBean GUIDs exactly
        fe.title(ep["title"])
        fe.description(ep["description"] or ep["title"])
        fe.published(parse_date(ep["published"]))
        fe.updated(parse_date(ep["published"]))
        fe.enclosure(ep["url"], str(ep["size"]), "audio/mpeg")
        fe.podcast.itunes_duration(ep["duration"])
        fe.podcast.itunes_explicit("no")


def add_spotify_fields(xml_bytes: bytes) -> bytes:
    """Port of what convert_feed.py used to inject — keeps Zinc happy."""
    ET.register_namespace("spotify", SPOTIFY_NS)
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")

    def set_or_update(parent, tag, value):
        existing = parent.find(tag)
        if existing is not None:
            existing.text = value
        else:
            ET.SubElement(parent, tag).text = value

    set_or_update(channel, f"{{{SPOTIFY_NS}}}limit", str(SPOTIFY_LIMIT))
    set_or_update(channel, f"{{{SPOTIFY_NS}}}countryOfOrigin", "il")
    for i, item in enumerate(channel.findall("item"), start=1):
        set_or_update(item, f"{{{SPOTIFY_NS}}}order", str(i))

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def main():
    known = json.loads(EPISODES_FILE.read_text(encoding="utf-8")) if EPISODES_FILE.exists() else {}
    episodes_sorted = sorted(known.values(), key=lambda x: x["published"], reverse=True)
    print(f"📚 Building feeds from {len(episodes_sorted)} episodes")

    # ── Zinc feed (feed.xml) — frozen name/URL, with spotify: fields ──────────
    fg_zinc = build_base_feed(FEED_URL_ZINC)
    add_episodes(fg_zinc, episodes_sorted)
    zinc_xml = add_spotify_fields(fg_zinc.rss_str(pretty=True))
    FEED_ZINC_FILE.write_bytes(zinc_xml)
    print(f"✅ {FEED_ZINC_FILE} written with {len(episodes_sorted)} episodes (Zinc / spotify: fields)")

    # ── Standard feed (feed-standard.xml) — clean, for Spotify/Apple ──────────
    fg_standard = build_base_feed(FEED_URL_STANDARD)
    add_episodes(fg_standard, episodes_sorted)
    fg_standard.rss_file(str(FEED_STANDARD_FILE), pretty=True)
    print(f"✅ {FEED_STANDARD_FILE} written with {len(episodes_sorted)} episodes (standard)")


if __name__ == "__main__":
    main()
