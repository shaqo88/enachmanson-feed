# enachmanson-feed

Legacy RSS feed repository for the Rabbi Elchanan Nachmanson podcast.

This repository is retired. The active podcast feed, sync, website, and
operations now live in
[`youtube-podcast-feeds`](https://github.com/shaqo88/youtube-podcast-feeds).
This repository can be archived after this retirement note is pushed.

## Feed URL

The active feed has moved to the generic podcast system:

```
https://torah-pod.pages.dev/nachmanson/feed.xml
```

The old feed remains online only as a historical migration pointer:

```
https://shaqo88.github.io/enachmanson-feed/feed.xml
```

## Migration

This repository has been migrated into
[`youtube-podcast-feeds`](https://github.com/shaqo88/youtube-podcast-feeds).
The old feed includes `itunes:new-feed-url`. Apple, Spotify, and Amazon Music
were already migrated to the Torah Pod feed before this repository was retired.
The PodBean account was deleted after migration, so PodBean evidence-capture
automation has been removed.

## How it works

The retired production pipeline was:

1. `yt/sync_episodes.py` reads the YouTube playlist.
2. New videos are downloaded and converted to 64 kbps MP3.
3. MP3 files are uploaded to Cloudflare R2.
4. Episode metadata is saved in `yt/episodes.json`.
5. `yt/build_feeds.py` generates the RSS feeds.
6. GitHub Pages served the legacy feed.

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

This repository has no active production automation. The active scheduled sync
runs from `youtube-podcast-feeds`.

The old PodBean migration evidence workflow was removed because the PodBean
account was deleted after cutover and no longer provides stable migration
evidence.

Legacy manual workflows may remain for historical recovery only:

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
