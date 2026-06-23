# enachmanson-feed

RSS feed for the Rabbi Elchanan Nachmanson podcast.

## Feed URL

```
https://shaqo88.github.io/enachmanson-feed/feed.xml
```

## Migration

See the [Podbean migration plan](docs/migration/MIGRATION_PLAN.md) for the
staged runbook and live status tracker.

## How it works

The production pipeline is:

1. `yt/sync_episodes.py` reads the YouTube playlist.
2. New videos are downloaded and converted to 64 kbps MP3.
3. MP3 files are uploaded to Cloudflare R2.
4. Episode metadata is saved in `yt/episodes.json`.
5. `yt/build_feeds.py` generates the RSS feeds.
6. GitHub Pages serves the canonical feed.

The source-controlled artwork is served from:

```
https://shaqo88.github.io/enachmanson-feed/assets/podcast-cover.png
```

## Generated feeds

- `feed.xml` is the canonical feed. Register only this URL with podcast
  directories.
- `feed-standard.xml` is an unregistered compatibility mirror generated from
  the same episode database.

## Automation

`Sync Episodes from YouTube` runs hourly at minute 17. It downloads new
episodes, uploads them to R2, rebuilds both feeds, validates the generated XML
and public media, and commits successful work.

If one episode fails, the script continues processing the remaining episodes,
persists successful uploads, and reports the workflow as failed after those
successful changes are committed.

The manual workflows are:

- `Rebuild Feeds Only`: rebuild and validate feeds from `episodes.json`.
- `Recover Episodes from R2`: compare R2 with `episodes.json` and optionally
  recover missing metadata.

## Repository secrets

- `YOUTUBE_PLAYLIST_ID`
- `YOUTUBE_COOKIES`
- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY`
- `R2_SECRET_KEY`
- `R2_BUCKET`
- `R2_PUBLIC_URL`
- `GMAIL_USER`
- `GMAIL_APP_PASSWORD`

## Local usage

```bash
# Install the exact workflow dependencies
python -m pip install -r requirements.txt

# Rebuild feeds from the checked-in episode database
python yt/build_feeds.py

# Validate XML, metadata, GUIDs, enclosures, and local artwork
python yt/validate_feed.py

# Also validate public artwork and byte-range playback for every enclosure
python yt/validate_feed.py --network
```
