# enachmanson-feed

Spotify-compatible RSS feed for the Rabbi Elchanan Nachmanson podcast.

## Feed URL

```
https://shaqo88.github.io/enachmanson-feed/feed.xml
```

This feed is auto-generated from the Podbean source:
`https://feed.podbean.com/enachmanson/feed.xml`

---

## How it works

`convert_feed.py` fetches the Podbean RSS feed and outputs `feed.xml` with a Spotify-compatible namespace structure. The file is hosted via GitHub Pages at the URL above.

---

## Auto-updates

A GitHub Actions workflow runs every hour, fetches the latest feed from Podbean, and commits an updated `feed.xml` automatically. No manual intervention needed.

To trigger a manual update: go to **Actions → Update Podcast Feed → Run workflow**.

---

## Local usage

```bash
python3 convert_feed.py
```

Outputs `feed.xml` in the current directory.
