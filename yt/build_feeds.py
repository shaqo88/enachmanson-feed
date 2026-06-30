#!/usr/bin/env python3
"""
Build the canonical RSS feed and an unregistered compatibility mirror.

Both feeds are generated from yt/episodes.json. The canonical URL, historical
episode GUIDs, and artwork URL are permanent migration identifiers.
"""

import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from feedgen.feed import FeedGenerator

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EPISODES_FILE = Path("yt/episodes.json")
FEED_CANONICAL_FILE = Path("feed.xml")
FEED_MIRROR_FILE = Path("feed-standard.xml")
ARTWORK_FILE = Path("assets/podcast-cover.png")

FEED_URL_CANONICAL = "https://shaqo88.github.io/enachmanson-feed/feed.xml"
FEED_URL_MIRROR = "https://shaqo88.github.io/enachmanson-feed/feed-standard.xml"
MIGRATED_FEED_URL = "https://shaqo88.github.io/youtube-podcast-feeds/nachmanson/feed.xml"
ARTWORK_URL = "https://shaqo88.github.io/enachmanson-feed/assets/podcast-cover.png"

PODCAST_TITLE = "שיעורי הרב אלחנן נחמנסון"
PODCAST_DESCRIPTION = (
    "כאן תשמעו שיעורי הלכה במגוון תחומים, שיעורים בחסידות בשפה השווה לכל נפש "
    "עם נגיעה לחיי היומיום, שיעורים בחינוך ושלום בית. בשיעוריו לוקח אותנו למסע "
    "המחבר את חיי המעשה עם התורה, כך שהתורה נהפכת לתורת חיים - מגלה רובד עמוק "
    "יותר בחיינו ופותחת צוהר להתרומם מעל אתגרי היומיום."
)
AUTHOR_NAME = "הרב אלחנן נחמנסון"
OWNER_NAME = "Torah Pod"
OWNER_EMAIL = "torahyoupod@gmail.com"
COPYRIGHT = "Copyright 2026 All rights reserved."

SPOTIFY_NS = "http://www.spotify.com/ns/rss"
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
SPOTIFY_LIMIT = 100


def parse_date(yyyymmdd: str) -> datetime:
    try:
        return datetime.strptime(yyyymmdd, "%Y%m%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime(2000, 1, 1, tzinfo=timezone.utc)


def build_base_feed(feed_url: str) -> FeedGenerator:
    feed = FeedGenerator()
    feed.load_extension("podcast")
    feed.id(feed_url)
    feed.title(PODCAST_TITLE)
    feed.description(PODCAST_DESCRIPTION)
    feed.author({"name": AUTHOR_NAME})
    feed.link(href=feed_url, rel="self")
    feed.language("he")
    feed.copyright(COPYRIGHT)
    feed.image(ARTWORK_URL)
    feed.podcast.itunes_category("Religion & Spirituality", "Judaism")
    feed.podcast.itunes_explicit("no")
    feed.podcast.itunes_author(AUTHOR_NAME)
    feed.podcast.itunes_image(ARTWORK_URL)
    return feed


def add_episodes(feed: FeedGenerator, episodes: list[dict]) -> None:
    for episode in episodes:
        entry = feed.add_entry()
        entry.id(f"yt:video:{episode['id']}")
        entry.title(episode["title"])
        entry.description(episode["description"] or episode["title"])
        entry.published(parse_date(episode["published"]))
        entry.updated(parse_date(episode["published"]))
        entry.enclosure(episode["url"], str(episode["size"]), "audio/mpeg")
        entry.podcast.itunes_duration(episode["duration"])
        entry.podcast.itunes_explicit("no")


def add_channel_metadata(xml_bytes: bytes, include_spotify: bool) -> bytes:
    """Inject migration metadata and optional Spotify compatibility fields."""
    ET.register_namespace("itunes", ITUNES_NS)
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
    ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")
    ET.register_namespace("spotify", SPOTIFY_NS)

    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("Generated RSS has no channel element")

    def set_or_update(parent: ET.Element, tag: str, value: str) -> None:
        element = parent.find(tag)
        if element is None:
            element = ET.SubElement(parent, tag)
        element.text = value

    def set_owner(parent: ET.Element) -> None:
        owner = parent.find(f"{{{ITUNES_NS}}}owner")
        if owner is None:
            owner = ET.SubElement(parent, f"{{{ITUNES_NS}}}owner")
        set_or_update(owner, f"{{{ITUNES_NS}}}name", OWNER_NAME)
        set_or_update(owner, f"{{{ITUNES_NS}}}email", OWNER_EMAIL)

    set_or_update(channel, f"{{{ITUNES_NS}}}type", "episodic")
    set_or_update(channel, f"{{{ITUNES_NS}}}summary", PODCAST_DESCRIPTION)
    set_or_update(channel, f"{{{ITUNES_NS}}}new-feed-url", MIGRATED_FEED_URL)
    set_owner(channel)

    if include_spotify:
        set_or_update(channel, f"{{{SPOTIFY_NS}}}limit", str(SPOTIFY_LIMIT))
        set_or_update(channel, f"{{{SPOTIFY_NS}}}countryOfOrigin", "il")
        for order, item in enumerate(channel.findall("item"), start=1):
            set_or_update(item, f"{{{SPOTIFY_NS}}}order", str(order))

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def write_feed(
    path: Path,
    feed_url: str,
    episodes: list[dict],
    include_spotify: bool,
) -> None:
    feed = build_base_feed(feed_url)
    add_episodes(feed, episodes)
    xml_bytes = add_channel_metadata(
        feed.rss_str(pretty=True),
        include_spotify=include_spotify,
    )
    path.write_bytes(xml_bytes)
    print(f"✅ {path} written with {len(episodes)} episodes")


def main() -> None:
    if not ARTWORK_FILE.exists():
        raise FileNotFoundError(f"Required artwork is missing: {ARTWORK_FILE}")

    known = (
        json.loads(EPISODES_FILE.read_text(encoding="utf-8"))
        if EPISODES_FILE.exists()
        else {}
    )
    available = [episode for episode in known.values() if not episode.get("unavailable")]
    episodes = sorted(available, key=lambda episode: episode["published"], reverse=True)
    print(f"📚 Building feeds from {len(episodes)} episodes")

    write_feed(
        FEED_CANONICAL_FILE,
        FEED_URL_CANONICAL,
        episodes,
        include_spotify=True,
    )
    write_feed(
        FEED_MIRROR_FILE,
        FEED_URL_MIRROR,
        episodes,
        include_spotify=False,
    )


if __name__ == "__main__":
    main()
