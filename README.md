# Podbean → Spotify RSS Feed Converter

## What this does
`convert_feed.py` fetches your Podbean RSS feed and outputs a `feed.xml` 
with Spotify-compatible namespace structure. Host `feed.xml` publicly 
(e.g. GitHub Pages) and share that URL.

---

## Setup: GitHub Pages (free, permanent URL)

### One-time setup
1. Create a new GitHub repo (e.g. `podcast-feed`)
2. Go to **Settings → Pages → Source**: select `main` branch, root folder
3. Your feed will be live at: `https://YOUR-USERNAME.github.io/podcast-feed/feed.xml`

### Files to put in the repo
```
podcast-feed/
├── convert_feed.py       ← the converter script
└── feed.xml              ← the generated feed (commit this after each run)
```

---

## Manual update workflow (now)

1. Edit `convert_feed.py` — update `PODBEAN_FEED_URL` if needed
2. Run: `python3 convert_feed.py`
3. Commit and push `feed.xml` to GitHub
4. Done — the URL stays the same

```bash
python3 convert_feed.py
git add feed.xml
git commit -m "Update feed"
git push
```

---

## Automatic updates (future): GitHub Actions

Create `.github/workflows/update_feed.yml` in your repo:

```yaml
name: Update Podcast Feed

on:
  schedule:
    - cron: '0 * * * *'   # every hour
  workflow_dispatch:        # also allow manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      - name: Run converter
        run: python3 convert_feed.py
      - name: Commit updated feed
        run: |
          git config user.email "actions@github.com"
          git config user.name "GitHub Actions"
          git add feed.xml
          git diff --cached --quiet || git commit -m "Auto-update feed"
          git push
```

This will automatically re-fetch your Podbean feed and push an updated 
`feed.xml` every hour — completely free, no server needed.

---

## Configuration

In `convert_feed.py`, edit these lines:
```python
PODBEAN_FEED_URL = "https://feed.podbean.com/enachmanson/feed.xml"
SPOTIFY_EMAIL = ""      # Optional: add your email if the platform requires it
SPOTIFY_LIMIT = 100     # Episodes per request
```
