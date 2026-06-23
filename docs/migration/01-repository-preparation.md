# Stage 1: Repository Preparation

Complete every item before starting the seven-day soak.

## Remove conflicting feed writers

- [ ] Disable or remove `.github/workflows/update_feed.yml`.
- [ ] Remove or archive `check_feed.py`, `convert_feed.py`, and
  `last_hash.txt`.
- [ ] Confirm no workflow other than the YouTube pipeline can overwrite
  `feed.xml`.
- [ ] Update `README.md` to describe:
  YouTube → MP3 → Cloudflare R2 → `episodes.json` → GitHub Pages RSS.
- [ ] Document `feed.xml` as the only canonical and registered feed.
- [ ] Document `feed-standard.xml` as an unregistered compatibility mirror.

## Preserve show metadata

- [ ] Preserve the final Podbean show's full description.
- [ ] Add `itunes:type` with the value `episodic`.
- [ ] Keep `itunes:explicit` set to `false`/`no`.
- [ ] Preserve the existing copyright value.
- [ ] Use stable artwork whose URL will not change during the migration.
- [ ] Add `itunes:new-feed-url` pointing to
  `https://shaqo88.github.io/enachmanson-feed/feed.xml`.
- [ ] Back up the artwork in source control or another independently
  recoverable location.

## Harden the workflows

- [ ] Add explicit `contents: write` permission.
- [ ] Pin Python and all Python dependencies to tested versions.
- [ ] Treat download and upload failures as workflow failures.
- [ ] Still persist and commit episodes that completed successfully before a
  later episode failed.
- [ ] Validate generated XML before committing.
- [ ] Reject duplicate or empty GUIDs.
- [ ] Validate every enclosure URL and content type.
- [ ] Validate artwork reachability, file type, and dimensions.
- [ ] Validate HTTP byte-range support for every enclosure.

## Correct recovery behavior

- [ ] Replace stale references to `sync_podcast.py` with the current scripts.
- [ ] Exclude entries marked `unavailable` when reporting
  `episodes.json` records that have no R2 object.

## Exit gate

Stage 1 is complete only when:

- the legacy pipeline cannot write the canonical feed;
- the generated feed contains the required metadata and migration tags;
- workflow failures are visible without losing successfully completed work;
- local and workflow validation checks pass.

Record completion in [STATUS.md](STATUS.md).
