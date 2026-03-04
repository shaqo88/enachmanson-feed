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

**`check_feed.py`** fetches the Podbean RSS feed and computes a SHA-256 hash, comparing it against the last known hash stored in `last_hash.txt`. If unchanged, the rest of the pipeline is skipped entirely.

**`convert_feed.py`** fetches the feed, converts it to a Spotify-compatible namespace structure, detects new, updated, and removed episodes, and writes `feed.xml`, `last_hash.txt`, and a commit message. The feed is hosted via GitHub Pages at the URL above.

---

## Auto-updates

A GitHub Actions workflow runs every hour and is split into four jobs:

| Job | What it does |
|---|---|
| `check` | Compares feed hash — skips remaining jobs if unchanged |
| `update` | Converts the feed and uploads artifacts |
| `commit` | Commits `feed.xml` and `last_hash.txt` to the repo |
| `notify` | Sends an email notification with the list of changes |

No manual intervention needed. When the feed is unchanged, only `check` runs — the other three jobs are skipped.

To trigger a manual update: go to **Actions → Update Podcast Feed → Run workflow**.

---

## Notifications

An email is sent to the repo owner whenever the feed is updated, showing exactly which episodes were added, updated, or removed.

Requires two GitHub repository secrets:
- `GMAIL_USER` — Gmail address to send and receive notifications
- `GMAIL_APP_PASSWORD` — [Gmail App Password](https://myaccount.google.com/apppasswords) (requires 2-Step Verification)

---

## Local usage

```bash
# Check if feed has changed
python3 check_feed.py

# Convert and update feed
python3 convert_feed.py
```

Both scripts output to the current directory. `convert_feed.py` writes `feed.xml` and `last_hash.txt`.
