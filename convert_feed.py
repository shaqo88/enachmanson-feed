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
SPOTIFY_EMAIL = ""          # Optional: add your email if the platform requires it
SPOTIFY_LIMIT = 100         # Max episodes Spotify fetches per request


def fetch_feed(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def convert(raw_xml: str) -> str:
    ET.register_namespace("", "")
    root = ET.fromstring(raw_xml)

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

    spotify_ns = "http://www.spotify.com/ns/rss"
    channel = root.find("channel")

    if SPOTIFY_EMAIL:
        email_tag = f"{{{spotify_ns}}}email"
        if channel.find(email_tag) is None:
            ET.SubElement(channel, email_tag).text = SPOTIFY_EMAIL

    limit_tag = f"{{{spotify_ns}}}limit"
    if channel.find(limit_tag) is None:
        ET.SubElement(channel, limit_tag).text = str(SPOTIFY_LIMIT)

    coo_tag = f"{{{spotify_ns}}}countryOfOrigin"
    if channel.find(coo_tag) is None:
        ET.SubElement(channel, coo_tag).text = "il"

    for i, item in enumerate(channel.findall("item"), start=1):
        order_tag = f"{{{spotify_ns}}}order"
        if item.find(order_tag) is None:
            ET.SubElement(item, order_tag).text = str(i)

    ET.register_namespace("content",    "http://purl.org/rss/1.0/modules/content/")
    ET.register_namespace("wfw",        "http://wellformedweb.org/CommentAPI/")
    ET.register_namespace("dc",         "http://purl.org/dc/elements/1.1/")
    ET.register_namespace("atom",       "http://www.w3.org/2005/Atom")
    ET.register_namespace("itunes",     "http://www.itunes.com/dtds/podcast-1.0.dtd")
    ET.register_namespace("googleplay", "http://www.google.com/schemas/play-podcasts/1.0")
    ET.register_namespace("spotify",    "http://www.spotify.com/ns/rss")
    ET.register_namespace("podcast",    "https://podcastindex.org/namespace/1.0")
    ET.register_namespace("media",      "http://search.yahoo.com/mrss/")

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


def main():
    print(f"Fetching {PODBEAN_FEED_URL} ...")
    raw = fetch_feed(PODBEAN_FEED_URL)
    new_root = ET.fromstring(raw)

    # Load and parse existing feed.xml directly into a tree for comparison
    existing_episodes = []
    if os.path.exists(OUTPUT_FILE):
        try:
            existing_episodes = extract_episodes(ET.parse(OUTPUT_FILE).getroot())
        except ET.ParseError:
            pass  # treat corrupt/missing file as empty

    new_episodes = extract_episodes(new_root)
    existing_by_guid = {ep["guid"]: ep for ep in existing_episodes}

    new_found = [ep for ep in new_episodes if ep["guid"] not in existing_by_guid]
    updated   = [
        ep for ep in new_episodes
        if ep["guid"] in existing_by_guid and ep != existing_by_guid[ep["guid"]]
    ]

    if not new_found and not updated:
        print("✅ No changes detected — skipping.")
        return

    # ── Build commit title ──
    if len(new_found) == 1 and not updated:
        commit_title = f"New episode: {new_found[0]['title']}"
    else:
        parts = []
        if new_found:
            parts.append(f"{len(new_found)} episode(s) added")
        if updated:
            parts.append(f"{len(updated)} episode(s) updated")
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

    print(f"🆕 {commit_title}")
    print(commit_body)

    # Write commit message for the workflow
    with open("commit_msg.txt", "w", encoding="utf-8") as f:
        f.write(commit_title + "\n\n" + commit_body)

    # Write GitHub Actions job summary if running in Actions
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(f"### {commit_title}\n\n")
            for line in lines:
                f.write(line + "  \n")

    # Write updated feed
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(convert(raw))

    print(f"✅ Feed updated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
