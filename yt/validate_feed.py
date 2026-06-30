#!/usr/bin/env python3
"""Validate generated podcast feeds and, optionally, public media."""

import argparse
import io
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import xml.etree.ElementTree as ET

import requests
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

EPISODES_FILE = Path("yt/episodes.json")
CANONICAL_FEED_FILE = Path("feed.xml")
MIRROR_FEED_FILE = Path("feed-standard.xml")
ARTWORK_FILE = Path("assets/podcast-cover.png")

CANONICAL_FEED_URL = "https://shaqo88.github.io/enachmanson-feed/feed.xml"
MIRROR_FEED_URL = "https://shaqo88.github.io/enachmanson-feed/feed-standard.xml"
MIGRATED_FEED_URL = "https://shaqo88.github.io/youtube-podcast-feeds/nachmanson/feed.xml"
ARTWORK_URL = "https://shaqo88.github.io/enachmanson-feed/assets/podcast-cover.png"

PODCAST_TITLE = "שיעורי הרב אלחנן נחמנסון"
PODCAST_DESCRIPTION = (
    "כאן תשמעו שיעורי הלכה במגוון תחומים, שיעורים בחסידות בשפה השווה לכל נפש "
    "עם נגיעה לחיי היומיום, שיעורים בחינוך ושלום בית. בשיעוריו לוקח אותנו למסע "
    "המחבר את חיי המעשה עם התורה, כך שהתורה נהפכת לתורת חיים - מגלה רובד עמוק "
    "יותר בחיינו ופותחת צוהר להתרומם מעל אתגרי היומיום."
)
OWNER_NAME = "Torah Pod"
OWNER_EMAIL = "torahyoupod@gmail.com"
COPYRIGHT = "Copyright 2026 All rights reserved."

ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ATOM_NS = "http://www.w3.org/2005/Atom"

MIN_ARTWORK_SIZE = 1400
MAX_ARTWORK_SIZE = 3000
HTTP_TIMEOUT = 30
NETWORK_WORKERS = 8


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def text(parent: ET.Element, path: str) -> str:
    node = parent.find(path)
    return (node.text or "").strip() if node is not None else ""


def load_available_episodes() -> dict:
    raw = json.loads(EPISODES_FILE.read_text(encoding="utf-8"))
    return {
        episode_id: episode
        for episode_id, episode in raw.items()
        if not episode.get("unavailable")
    }


def validate_artwork_image(image: Image.Image, source: str) -> None:
    width, height = image.size
    require(width == height, f"{source}: artwork must be square, got {width}x{height}")
    require(
        MIN_ARTWORK_SIZE <= width <= MAX_ARTWORK_SIZE,
        f"{source}: artwork must be {MIN_ARTWORK_SIZE}-{MAX_ARTWORK_SIZE}px, got {width}px",
    )


def validate_local_artwork() -> None:
    require(ARTWORK_FILE.exists(), f"Missing artwork: {ARTWORK_FILE}")
    with Image.open(ARTWORK_FILE) as image:
        image.verify()
    with Image.open(ARTWORK_FILE) as image:
        validate_artwork_image(image, str(ARTWORK_FILE))
    print(f"✅ Artwork is valid: {ARTWORK_FILE}")


def parse_feed(path: Path) -> ET.Element:
    require(path.exists(), f"Missing feed: {path}")
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"{path}: invalid XML: {exc}") from exc
    channel = root.find("channel")
    require(channel is not None, f"{path}: missing channel")
    return channel


def validate_feed(path: Path, expected_self_url: str, episodes: dict) -> dict:
    channel = parse_feed(path)

    require(text(channel, "title") == PODCAST_TITLE, f"{path}: incorrect title")
    require(
        text(channel, "description") == PODCAST_DESCRIPTION,
        f"{path}: incorrect show description",
    )
    require(text(channel, "copyright") == COPYRIGHT, f"{path}: incorrect copyright")
    require(
        text(channel, f"{{{ITUNES_NS}}}type") == "episodic",
        f"{path}: itunes:type must be episodic",
    )
    require(
        text(channel, f"{{{ITUNES_NS}}}explicit").lower() in {"false", "no"},
        f"{path}: itunes:explicit must be false/no",
    )
    require(
        text(channel, f"{{{ITUNES_NS}}}new-feed-url") == MIGRATED_FEED_URL,
        f"{path}: itunes:new-feed-url must be the migrated feed",
    )
    require(
        text(channel, f"{{{ITUNES_NS}}}summary") == PODCAST_DESCRIPTION,
        f"{path}: itunes:summary must preserve the show description",
    )
    owner = channel.find(f"{{{ITUNES_NS}}}owner")
    require(owner is not None, f"{path}: missing itunes:owner")
    require(
        text(owner, f"{{{ITUNES_NS}}}name") == OWNER_NAME,
        f"{path}: itunes:owner name must be {OWNER_NAME}",
    )
    require(
        text(owner, f"{{{ITUNES_NS}}}email") == OWNER_EMAIL,
        f"{path}: itunes:owner email must be {OWNER_EMAIL}",
    )

    self_urls = {
        link.get("href")
        for link in channel.findall(f"{{{ATOM_NS}}}link")
        if link.get("rel") == "self"
    }
    require(
        expected_self_url in self_urls,
        f"{path}: atom self link must be {expected_self_url}",
    )

    itunes_image = channel.find(f"{{{ITUNES_NS}}}image")
    require(itunes_image is not None, f"{path}: missing itunes:image")
    require(
        itunes_image.get("href") == ARTWORK_URL,
        f"{path}: artwork URL must be {ARTWORK_URL}",
    )
    rss_image = channel.find("image/url")
    require(
        rss_image is not None and (rss_image.text or "").strip() == ARTWORK_URL,
        f"{path}: RSS artwork URL must be {ARTWORK_URL}",
    )

    items = channel.findall("item")
    require(
        len(items) == len(episodes),
        f"{path}: expected {len(episodes)} items, found {len(items)}",
    )

    guids = []
    enclosures = {}
    for item in items:
        guid = text(item, "guid")
        require(guid, f"{path}: item has an empty GUID")
        require(guid.startswith("yt:video:"), f"{path}: unexpected GUID format: {guid}")
        episode_id = guid.removeprefix("yt:video:")
        require(episode_id in episodes, f"{path}: unknown episode GUID: {guid}")

        enclosure = item.find("enclosure")
        require(enclosure is not None, f"{path}: {guid} has no enclosure")
        require(
            enclosure.get("url") == episodes[episode_id]["url"],
            f"{path}: {guid} enclosure URL does not match episodes.json",
        )
        require(
            enclosure.get("length") == str(episodes[episode_id]["size"]),
            f"{path}: {guid} enclosure length does not match episodes.json",
        )
        require(
            enclosure.get("type") == "audio/mpeg",
            f"{path}: {guid} enclosure type must be audio/mpeg",
        )
        guids.append(guid)
        enclosures[guid] = enclosure.get("url")

    require(len(guids) == len(set(guids)), f"{path}: duplicate GUIDs found")
    require(
        len(enclosures.values()) == len(set(enclosures.values())),
        f"{path}: duplicate enclosure URLs found",
    )
    print(f"✅ {path}: {len(items)} items, unique GUIDs and enclosures")
    return enclosures


def validate_public_feed(expected_guids: set[str]) -> None:
    response = requests.get(CANONICAL_FEED_URL, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "").lower()
    require("xml" in content_type, f"Canonical feed content type is {content_type!r}")
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as exc:
        raise ValueError(f"Published canonical feed is invalid XML: {exc}") from exc
    channel = root.find("channel")
    require(channel is not None, "Published canonical feed has no channel")
    public_guids = {text(item, "guid") for item in channel.findall("item")}
    require(
        public_guids == expected_guids,
        "Published canonical feed GUIDs do not match the generated feed",
    )
    require(
        text(channel, f"{{{ITUNES_NS}}}new-feed-url") == MIGRATED_FEED_URL,
        "Published canonical feed has the wrong itunes:new-feed-url",
    )
    owner = channel.find(f"{{{ITUNES_NS}}}owner")
    require(
        owner is not None and text(owner, f"{{{ITUNES_NS}}}email") == OWNER_EMAIL,
        "Published canonical feed has the wrong owner email",
    )
    itunes_image = channel.find(f"{{{ITUNES_NS}}}image")
    require(
        itunes_image is not None and itunes_image.get("href") == ARTWORK_URL,
        "Published canonical feed has the wrong artwork URL",
    )
    print(f"✅ Published canonical feed is current: {CANONICAL_FEED_URL}")


def validate_public_artwork() -> None:
    response = requests.get(ARTWORK_URL, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "").lower()
    require(content_type.startswith("image/"), f"Artwork content type is {content_type!r}")
    with Image.open(io.BytesIO(response.content)) as image:
        image.verify()
    with Image.open(io.BytesIO(response.content)) as image:
        validate_artwork_image(image, ARTWORK_URL)
    print(f"✅ Public artwork is reachable and valid: {ARTWORK_URL}")


def validate_enclosure(url: str) -> str:
    response = requests.get(
        url,
        headers={"Range": "bytes=0-0"},
        timeout=HTTP_TIMEOUT,
        stream=True,
    )
    try:
        require(response.status_code == 206, f"range request returned {response.status_code}")
        content_type = response.headers.get("Content-Type", "").lower()
        require(
            content_type.startswith("audio/mpeg"),
            f"unexpected content type {content_type!r}",
        )
        content_range = response.headers.get("Content-Range", "")
        require(
            content_range.startswith("bytes 0-0/"),
            f"invalid Content-Range {content_range!r}",
        )
        next(response.iter_content(chunk_size=1), b"")
    finally:
        response.close()
    return url


def validate_public_enclosures(urls: set[str]) -> None:
    failures = []
    with ThreadPoolExecutor(max_workers=NETWORK_WORKERS) as executor:
        future_urls = {executor.submit(validate_enclosure, url): url for url in urls}
        for future in as_completed(future_urls):
            url = future_urls[future]
            try:
                future.result()
            except Exception as exc:
                failures.append(f"{url}: {exc}")
    require(not failures, "Enclosure validation failed:\n" + "\n".join(failures))
    print(f"✅ {len(urls)} public enclosures support byte-range playback")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--network",
        action="store_true",
        help="Also validate public artwork and every enclosure with HTTP range requests",
    )
    args = parser.parse_args()

    try:
        episodes = load_available_episodes()
        validate_local_artwork()
        canonical = validate_feed(CANONICAL_FEED_FILE, CANONICAL_FEED_URL, episodes)
        mirror = validate_feed(MIRROR_FEED_FILE, MIRROR_FEED_URL, episodes)
        require(canonical == mirror, "Canonical feed and mirror contain different episodes")
        print("✅ Canonical feed and compatibility mirror contain identical episodes")

        if args.network:
            validate_public_feed(set(canonical))
            validate_public_artwork()
            validate_public_enclosures(set(canonical.values()))
    except (OSError, ValueError, requests.RequestException) as exc:
        print(f"❌ Validation failed: {exc}", file=sys.stderr)
        return 1

    print("✅ Feed validation complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
