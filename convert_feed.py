#!/usr/bin/env python3
"""
Podbean → Spotify RSS Feed Converter
Fetches your Podbean RSS feed and outputs a Spotify for Podcasters-compatible feed.
Usage: python3 convert_feed.py
Output: feed.xml  (host this file publicly, e.g. via GitHub Pages)
"""

import os
import urllib.request
import xml.etree.ElementTree as ET

PODBEAN_FEED_URL = "https://feed.podbean.com/enachmanson/feed.xml"
OUTPUT_FILE = "feed.xml"

# ── Spotify-specific fields to add/ensure ──────────────────────────────────
# Edit these if needed
SPOTIFY_EMAIL = ""          # Required by some platforms; add your email here
SPOTIFY_LIMIT = 100         # Max episodes Spotify fetches per request

def fetch_feed(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")

def convert(raw_xml: str) -> str:
    # Parse
    ET.register_namespace("", "")   # avoid default ns mangling
    root = ET.fromstring(raw_xml)

    # ── Namespaces present in the Podbean feed ──
    ns = {
        "itunes":     "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "spotify":    "http://www.spotify.com/ns/rss",
        "content":    "http://purl.org/rss/1.0/modules/content/",
        "atom":       "http://www.w3.org/2005/Atom",
        "dc":         "http://purl.org/dc/elements/1.1/",
        "googleplay": "http://www.google.com/schemas/play-podcasts/1.0",
        "podcast":    "https://podcastindex.org/namespace/1.0",
        "media":      "http://search.yahoo.com/mrss/",
    }

    channel = root.find("channel")

    # ── 1. Ensure spotify namespace declarations are on root ──
    spotify_ns_attrs = {
        "xmlns:content":    "http://purl.org/rss/1.0/modules/content/",
        "xmlns:wfw":        "http://wellformedweb.org/CommentAPI/",
        "xmlns:dc":         "http://purl.org/dc/elements/1.1/",
        "xmlns:atom":       "http://www.w3.org/2005/Atom",
        "xmlns:itunes":     "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "xmlns:googleplay": "http://www.google.com/schemas/play-podcasts/1.0",
        "xmlns:spotify":    "http://www.spotify.com/ns/rss",
        "xmlns:podcast":    "https://podcastindex.org/namespace/1.0",
        "xmlns:media":      "http://search.yahoo.com/mrss/",
    }

    # ── 2. Add spotify:email if configured ──
    spotify_ns = "http://www.spotify.com/ns/rss"
    if SPOTIFY_EMAIL:
        email_tag = f"{{{spotify_ns}}}email"
        if channel.find(email_tag) is None:
            email_el = ET.SubElement(channel, email_tag)
            email_el.text = SPOTIFY_EMAIL

    # ── 3. Ensure spotify:limit ──
    limit_tag = f"{{{spotify_ns}}}limit"
    if channel.find(limit_tag) is None:
        limit_el = ET.SubElement(channel, limit_tag)
        limit_el.text = str(SPOTIFY_LIMIT)

    # ── 4. Ensure spotify:countryOfOrigin exists ──
    coo_tag = f"{{{spotify_ns}}}countryOfOrigin"
    if channel.find(coo_tag) is None:
        coo_el = ET.SubElement(channel, coo_tag)
        coo_el.text = "il"

    # ── 5. Per-episode: ensure spotify:order ──
    items = channel.findall("item")
    for i, item in enumerate(items, start=1):
        order_tag = f"{{{spotify_ns}}}order"
        if item.find(order_tag) is None:
            order_el = ET.SubElement(item, order_tag)
            order_el.text = str(i)

    # ── Serialize ──
    # Re-build with correct namespace declarations on <rss>
    ET.register_namespace("content",    "http://purl.org/rss/1.0/modules/content/")
    ET.register_namespace("wfw",        "http://wellformedweb.org/CommentAPI/")
    ET.register_namespace("dc",         "http://purl.org/dc/elements/1.1/")
    ET.register_namespace("atom",       "http://www.w3.org/2005/Atom")
    ET.register_namespace("itunes",     "http://www.itunes.com/dtds/podcast-1.0.dtd")
    ET.register_namespace("googleplay", "http://www.google.com/schemas/play-podcasts/1.0")
    ET.register_namespace("spotify",    "http://www.spotify.com/ns/rss")
    ET.register_namespace("podcast",    "https://podcastindex.org/namespace/1.0")
    ET.register_namespace("media",      "http://search.yahoo.com/mrss/")

    output = ET.tostring(root, encoding="unicode", xml_declaration=False)

    # Prepend proper XML declaration
    output = '<?xml version="1.0" encoding="UTF-8"?>\n' + output

    # Fix the <rss> tag to include all namespace declarations explicitly
    # (ElementTree sometimes drops unused ones)
    rss_open = '<rss version="2.0"'
    ns_block = " ".join(f'{k}="{v}"' for k, v in spotify_ns_attrs.items())
    output = output.replace(
        '<rss version="2.0"',
        f'<rss version="2.0"\n     {ns_block}'
    )

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


PUBDATE_FILE = "last_pubdate.txt"


def main():
    print(f"Fetching {PODBEAN_FEED_URL} ...")
    raw = fetch_feed(PODBEAN_FEED_URL)

    # ── Early exit: compare channel pubDate before doing any real work ──
    new_root = ET.fromstring(raw)
    channel_pubdate = new_root.findtext("channel/pubDate", "").strip()

    if os.path.exists(PUBDATE_FILE):
        saved = open(PUBDATE_FILE).read().strip()
        if saved == channel_pubdate:
            print(f"✅ Feed pubDate unchanged ({channel_pubdate}) — skipping.")
            return

    print(f"📡 Feed pubDate changed → {channel_pubdate}, processing ...")

    # Load and parse existing feed.xml directly — no string comparison
    existing_episodes = []
    if os.path.exists(OUTPUT_FILE):
        try:
            existing_episodes = extract_episodes(ET.parse(OUTPUT_FILE).getroot())
        except ET.ParseError:
            pass  # treat corrupt/missing file as empty

    new_episodes = extract_episodes(new_root)

    existing_by_guid = {ep["guid"]: ep for ep in existing_episodes}

    new_found   = [ep for ep in new_episodes if ep["guid"] not in existing_by_guid]
    updated     = [
        ep for ep in new_episodes
        if ep["guid"] in existing_by_guid and ep != existing_by_guid[ep["guid"]]
    ]

    if not new_found and not updated:
        print("✅ No new episodes — feed unchanged, skipping write.")
        return

    # ── Build commit title ──
    parts = []
    if new_found:
        parts.append(f"{len(new_found)} episode(s) added")
    if updated:
        parts.append(f"{len(updated)} episode(s) updated")

    if len(new_found) == 1 and not updated:
        commit_title = f"New episode: {new_found[0]['title']}"
    else:
        commit_title = ", ".join(parts)

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

    commit_body = "\n".join(lines)

    # Print to Actions log
    print(f"🆕 {commit_title}")
    print(commit_body)

    # Write commit message to file for the workflow to read
    with open("commit_msg.txt", "w", encoding="utf-8") as f:
        f.write(commit_title + "\n\n" + commit_body)

    # Write updated feed
    converted = convert(raw)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(converted)

    with open(PUBDATE_FILE, "w") as f:
        f.write(channel_pubdate)

    print(f"✅ Feed updated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
