#!/usr/bin/env python3
"""
Podbean → Spotify RSS Feed Converter
Fetches your Podbean RSS feed and outputs a Spotify for Podcasters-compatible feed.
Usage: python3 convert_feed.py
Output: feed.xml  (host this file publicly, e.g. via GitHub Pages)
"""

import hashlib
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

PODBEAN_FEED_URL = "https://feed.podbean.com/enachmanson/feed.xml"
OUTPUT_FILE      = "feed.xml"
HASH_FILE        = "last_hash.txt"

# ── Spotify-specific fields to add/ensure ──────────────────────────────────
SPOTIFY_EMAIL = ""          # Optional: add your email if the platform requires it
SPOTIFY_LIMIT = 100         # Max episodes Spotify fetches per request

NAMESPACES = {
    "content":    "http://purl.org/rss/1.0/modules/content/",
    "wfw":        "http://wellformedweb.org/CommentAPI/",
    "dc":         "http://purl.org/dc/elements/1.1/",
    "atom":       "http://www.w3.org/2005/Atom",
    "itunes":     "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "googleplay": "http://www.google.com/schemas/play-podcasts/1.0",
    "spotify":    "http://www.spotify.com/ns/rss",
    "podcast":    "https://podcastindex.org/namespace/1.0",
    "media":      "http://search.yahoo.com/mrss/",
}


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


def set_or_update(parent: ET.Element, tag: str, value: str):
    """Set a child element's text, updating it if it already exists."""
    existing = parent.find(tag)
    if existing is not None:
        existing.text = value
    else:
        ET.SubElement(parent, tag).text = value


def convert(raw_xml: str) -> str:
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)

    root = ET.fromstring(raw_xml)
    spotify_ns_attrs = {f"xmlns:{k}": v for k, v in NAMESPACES.items()}
    spotify_ns = NAMESPACES["spotify"]
    channel = root.find("channel")

    if SPOTIFY_EMAIL:
        set_or_update(channel, f"{{{spotify_ns}}}email", SPOTIFY_EMAIL)

    set_or_update(channel, f"{{{spotify_ns}}}limit", str(SPOTIFY_LIMIT))
    set_or_update(channel, f"{{{spotify_ns}}}countryOfOrigin", "il")

    for i, item in enumerate(channel.findall("item"), start=1):
        set_or_update(item, f"{{{spotify_ns}}}order", str(i))

    output = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")
    ns_block = " ".join(f'{k}="{v}"' for k, v in spotify_ns_attrs.items())
    output = output.replace('<rss version="2.0"', f'<rss version="2.0"\n     {ns_block}')
    return output


def extract_episodes(root: ET.Element) -> list:
    """Extract episode GUIDs, titles and pubDates from a parsed XML tree."""
    channel = root.find("channel")
    return [
        {
            "guid":    item.findtext("guid", ""),
            "title":   item.findtext("title", ""),
            "pubDate": item.findtext("pubDate", ""),
        }
        for item in channel.findall("item")
    ]


def write_summary(text: str):
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(text)


def main():
    print(f"Fetching {PODBEAN_FEED_URL} ...")
    raw = fetch_feed(PODBEAN_FEED_URL)
    new_root = ET.fromstring(raw)

    # Load and parse existing feed.xml for comparison
    existing_episodes = []
    if os.path.exists(OUTPUT_FILE):
        try:
            existing_episodes = extract_episodes(ET.parse(OUTPUT_FILE).getroot())
        except ET.ParseError:
            pass  # treat corrupt/missing file as empty

    new_episodes     = extract_episodes(new_root)
    existing_by_guid = {ep["guid"]: ep for ep in existing_episodes}
    new_by_guid      = {ep["guid"]: ep for ep in new_episodes}

    new_found = [ep for ep in new_episodes if ep["guid"] not in existing_by_guid]
    updated   = [
        ep for ep in new_episodes
        if ep["guid"] in existing_by_guid and ep != existing_by_guid[ep["guid"]]
    ]
    removed   = [ep for ep in existing_episodes if ep["guid"] not in new_by_guid]

    total = len(new_episodes)

    # ── Build commit title ──
    if len(new_found) == 1 and not updated and not removed:
        commit_title = f"New episode: {new_found[0]['title']}"
    else:
        parts = []
        if new_found:
            parts.append(f"{len(new_found)} episode(s) added")
        if updated:
            parts.append(f"{len(updated)} episode(s) updated")
        if removed:
            parts.append(f"{len(removed)} episode(s) removed")
        commit_title = ", ".join(parts) if parts else "Feed refreshed"

    # ── Build commit description ──
    lines = []
    if new_found:
        lines.append("New episodes:")
        for ep in new_found:
            lines.append(f"  + {ep['title']} ({ep['pubDate']})")
    if updated:
        lines.append("Updated episodes:")
        for ep in updated:
            old_ep = existing_by_guid[ep["guid"]]
            lines.append(f"  ~ {ep['title']} ({ep['pubDate']})")
            if old_ep["title"] != ep["title"]:
                lines.append(f"      title:   {old_ep['title']} → {ep['title']}")
            if old_ep["pubDate"] != ep["pubDate"]:
                lines.append(f"      pubDate: {old_ep['pubDate']} → {ep['pubDate']}")
    if removed:
        lines.append("Removed episodes:")
        for ep in removed:
            lines.append(f"  - {ep['title']} ({ep['pubDate']})")

    commit_body = "\n".join(lines)

    print(f"🆕 {commit_title}")
    print(commit_body)

    # Write commit message for the workflow
    with open("commit_msg.txt", "w", encoding="utf-8") as f:
        f.write(commit_title + "\n\n" + commit_body)

    # Write GitHub Actions job summary
    summary_lines = [f"### 📻 {commit_title} ({total} episodes total)\n\n"]
    for line in lines:
        summary_lines.append(line + "  \n")
    write_summary("".join(summary_lines))

    # Write updated feed
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(convert(raw))

    # Write updated hash so it gets committed alongside feed.xml
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(compute_hash(raw))

    print(f"✅ Feed updated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
