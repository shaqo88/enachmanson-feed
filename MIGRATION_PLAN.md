# Podbean Migration Review and Runbook

## Decision

The migration design is sound, but **do not cancel Podbean yet**.

The most important continuity requirement has been met: all 79 historical
episode GUIDs exactly match between the final Podbean-derived feed and the new
feed. Changing these GUIDs would cause podcast applications to treat existing
episodes as new or duplicate episodes.

The canonical feed for every podcast directory is:

<https://shaqo88.github.io/enachmanson-feed/feed.xml>

`feed-standard.xml` is an unregistered compatibility mirror only. Do not submit
it to Spotify, Apple Podcasts, or any other directory.

## Verified baseline

The repository and generated feed were reviewed with the following results:

| Check | Result |
| --- | --- |
| Historical GUID comparison | 79 of 79 match the final Podbean-derived feed |
| Canonical feed | Serves successfully |
| Feed episodes | 79 |
| Unique GUIDs | 79 |
| Unique enclosure URLs | 79 |
| R2 audio referenced by the feed | 934,481,955 bytes (0.87 GiB) |
| Unavailable YouTube inventory entries | 4, intentionally excluded from the feed |

## Current blockers

Do not start the cutover until the repository-preparation work and one-week soak
below are complete.

- Only one scheduled production run had completed at the time of the migration
  review. There is not yet enough evidence of unattended reliability.
- The audio uses an `r2.dev` public endpoint. Cloudflare documents this endpoint
  as intended for non-production use.
- The legacy Podbean workflow remains present and can still overwrite
  `feed.xml`.
- Show metadata and migration tags are incomplete.
- HTTP byte-range playback for every audio object and the artwork dimensions
  have not been externally validated.
- A two-week total migration would conflict with Apple's requirement to keep
  the redirect and `itunes:new-feed-url` available for at least four weeks.

## Repository preparation

Complete these changes before starting the soak period:

- [ ] Disable or remove `.github/workflows/update_feed.yml`.
- [ ] Remove or archive `check_feed.py`, `convert_feed.py`, and
  `last_hash.txt` so the Podbean-derived pipeline cannot overwrite the
  YouTube-generated feed.
- [ ] Update `README.md` to describe the actual pipeline:
  YouTube → MP3 → Cloudflare R2 → `episodes.json` → GitHub Pages RSS.
- [ ] Make `feed.xml` the only canonical and registered feed.
- [ ] Keep `feed-standard.xml` only as an unregistered compatibility mirror.
- [ ] Preserve the final Podbean show's full description.
- [ ] Add `itunes:type` with the value `episodic`.
- [ ] Keep `itunes:explicit` set to `false`/`no`.
- [ ] Preserve the existing copyright value.
- [ ] Use stable artwork whose URL will not change during the migration.
- [ ] Add `itunes:new-feed-url` pointing to
  `https://shaqo88.github.io/enachmanson-feed/feed.xml`.
- [ ] Back up the artwork in source control or another independently
  recoverable location.

### Workflow hardening

Apply the following changes to the production sync workflow:

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
- [ ] Correct recovery documentation that still refers to
  `sync_podcast.py`.
- [ ] Exclude entries marked `unavailable` when reporting
  `episodes.json` records that have no R2 object.

## One-week soak

Run the prepared production system for seven consecutive days before cutover.
Restart the seven-day clock after a material feed-generation or sync fix.

### Required evidence

- [ ] Every hourly scheduled run succeeds for seven consecutive days.
- [ ] At least one genuinely new episode completes the full path:
  YouTube → MP3 → R2 → RSS.
- [ ] The new episode plays from the canonical feed.
- [ ] The canonical feed remains available throughout the soak.
- [ ] All 79 historical enclosure URLs return successfully.
- [ ] Every enclosure supports ranged playback.
- [ ] The artwork is reachable, square, and between 1400 and 3000 pixels.
- [ ] The feed is valid XML and passes a podcast feed validator.
- [ ] All 79 historical GUIDs remain unchanged and unique.
- [ ] The `r2.dev` production warning is recorded as accepted temporary risk.
- [ ] A future migration to an R2 custom domain is tracked separately.

### Preserve before cutover

Store these outside Podbean as well as in the migration records:

- [ ] Final Podbean RSS XML snapshot.
- [ ] Podbean analytics export.
- [ ] URLs for every known podcast listing.
- [ ] Account owner, login-recovery, and billing ownership details for each
  directory.
- [ ] A copy of the final artwork.

## Cutover procedure

Record the cutover date and time before making changes:

| Field | Value |
| --- | --- |
| Cutover date/time | |
| Operator | |
| Final Podbean feed URL | |
| Canonical feed URL | `https://shaqo88.github.io/enachmanson-feed/feed.xml` |
| Earliest Podbean cancellation date | Cutover date + 28 days |

### 1. Configure the Podbean redirect

1. In Podbean, open **Settings → Feed → Advanced Feed Settings**.
2. Enter the canonical URL in **Redirect to a New Feed**:
   `https://shaqo88.github.io/enachmanson-feed/feed.xml`.
3. Save the change.
4. Verify the old Podbean feed returns HTTP **301**, not 302.
5. Verify the `Location` header is the exact canonical URL, with no
   intermediate redirect.

Do not proceed if the old feed does not return the correct permanent redirect.

### 2. Update Spotify for Creators

1. Open the existing podcast in Spotify for Creators.
2. Go to **Settings**.
3. Select **Update** beside the current RSS feed.
4. Enter the canonical URL.
5. Confirm the hosting provider and complete Spotify's verification.

Update the existing show. Do not create or submit a duplicate show.

### 3. Confirm Apple Podcasts migration

Allow the Podbean 301 redirect and `itunes:new-feed-url` to migrate the existing
show.

1. Open the existing show in Apple Podcasts Connect.
2. Confirm that Apple recognizes the canonical feed.
3. Confirm that the show and its episodes remain attached to the existing
   listing.

Do not submit a new show.

### 4. Verify other directories

Check all known listings, including:

- Amazon Music
- Pocket Casts
- Overcast
- Castbox
- Podcast Index
- TuneIn
- Any directory recorded in the pre-cutover inventory

Allow each directory to follow the 301 redirect. Update its dashboard directly
only if it does not migrate automatically.

### 5. Playback checks

In every major application:

- [ ] Play the oldest episode.
- [ ] Play the newest episode.
- [ ] Seek forward within each episode to exercise byte-range playback.
- [ ] Confirm there is one show listing, not a duplicate.
- [ ] Confirm there are no duplicate historical episodes.

## Post-cutover checkpoints

### One week after cutover

Perform a health checkpoint, but **do not cancel Podbean**.

- [ ] The old feed still returns a permanent 301 to the canonical feed.
- [ ] Spotify and Apple use the canonical feed.
- [ ] Other known directories have migrated or were updated directly.
- [ ] No duplicate show or duplicate episodes are visible.
- [ ] A post-cutover episode reached existing followers automatically.
- [ ] Feed and audio availability have remained stable.

### Four weeks after cutover

Apple requires the redirect and `itunes:new-feed-url` to remain available for
at least four weeks. The earliest supported Podbean cancellation date is
therefore **28 days after cutover**, and only after all acceptance tests pass.

Before cancellation:

- [ ] Confirm with Podbean support whether the 301 redirect survives downgrade
  or cancellation.
- [ ] If the redirect would stop, retain the lowest suitable Podbean plan
  through the full four-week window.
- [ ] Re-run all platform and playback verification.
- [ ] Export any final analytics or account records.

## Acceptance tests

All checks must pass before the migration is considered complete:

- [ ] The old Podbean URL returns a permanent HTTP 301 to the exact canonical
  feed.
- [ ] The canonical feed returns HTTP 200 with an XML content type.
- [ ] Exactly 79 historical GUIDs remain unchanged and unique.
- [ ] All 79 historical audio URLs return successfully.
- [ ] All audio URLs support ranged playback.
- [ ] Artwork is reachable, square, and 1400–3000 pixels.
- [ ] Spotify shows no duplicate podcast or duplicate episodes.
- [ ] Apple Podcasts shows no duplicate podcast or duplicate episodes.
- [ ] Existing followers receive a post-cutover episode automatically.
- [ ] The seven-day soak completed without feed outages.
- [ ] The four-week redirect period completed without feed outages.

## Permanent invariants

After migration:

- Never rename the GitHub account.
- Never rename the repository.
- Never change the canonical `feed.xml` path.
- Never recycle or rewrite an episode GUID.
- Do not register `feed-standard.xml` with a podcast directory.

## References

- [Apple: Change the RSS feed URL](https://podcasters.apple.com/support/837-change-the-rss-feed-url)
- [Apple: Validate your podcast](https://podcasters.apple.com/support/829-validate-your-podcast)
- [Spotify: Update an RSS feed link or hosting provider](https://support.spotify.com/us/creators/article/updating-an-rss-feed-link-or-hosting-provider/)
- [Podbean: Set a 301 feed redirect](https://help.podbean.com/support/solutions/articles/25000013419-setting-a-301-feed-redirect)
- [Cloudflare: R2 public buckets and public development URLs](https://developers.cloudflare.com/r2/buckets/public-buckets/)
