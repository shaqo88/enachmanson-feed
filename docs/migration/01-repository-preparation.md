# Stage 1: Repository Preparation

Complete every item before starting the seven-day soak.

## Remove conflicting feed writers

- [x] Disable or remove `.github/workflows/update_feed.yml`.
- [x] Remove or archive `check_feed.py`, `convert_feed.py`, and
  `last_hash.txt`.
- [x] Confirm no workflow other than the YouTube pipeline can overwrite
  `feed.xml`.
- [x] Update `README.md` to describe:
  YouTube → MP3 → Cloudflare R2 → `episodes.json` → GitHub Pages RSS.
- [x] Document `feed.xml` as the only canonical and registered feed.
- [x] Document `feed-standard.xml` as an unregistered compatibility mirror.

## Preserve show metadata

- [x] Preserve the final Podbean show's full description.
- [x] Add `itunes:type` with the value `episodic`.
- [x] Keep `itunes:explicit` set to `false`/`no`.
- [x] Preserve the existing copyright value.
- [x] Use stable artwork whose URL will not change during the migration.
- [x] Add `itunes:new-feed-url` pointing to
  `https://shaqo88.github.io/enachmanson-feed/feed.xml`.
- [x] Back up the artwork in source control or another independently
  recoverable location.

## Harden the workflows

- [x] Add explicit `contents: write` permission.
- [x] Pin Python and all Python dependencies to tested versions.
- [x] Treat download and upload failures as workflow failures.
- [x] Still persist and commit episodes that completed successfully before a
  later episode failed.
- [x] Validate generated XML before committing.
- [x] Reject duplicate or empty GUIDs.
- [x] Validate every enclosure URL and content type.
- [x] Validate artwork reachability, file type, and dimensions.
- [x] Validate HTTP byte-range support for every enclosure.

## Correct recovery behavior

- [x] Replace stale references to `sync_podcast.py` with the current scripts.
- [x] Exclude entries marked `unavailable` when reporting
  `episodes.json` records that have no R2 object.

Implementation completed locally on June 23, 2026. The Stage 1 exit gate remains
open until the hardened workflow completes successfully on GitHub Actions.

## Exit gate

Stage 1 is complete only when:

- the legacy pipeline cannot write the canonical feed;
- the generated feed contains the required metadata and migration tags;
- workflow failures are visible without losing successfully completed work;
- local and workflow validation checks pass.

Record completion in [STATUS.md](STATUS.md).
