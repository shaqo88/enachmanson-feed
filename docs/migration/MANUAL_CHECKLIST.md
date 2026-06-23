# Manual Migration Checklist

Automation covers feed health, all 79 enclosure range checks, artwork,
scheduled-run monitoring, Podbean/canonical RSS snapshots, GUID comparison, and
Apple public-directory discovery.

## Completed

- [x] Export Podbean analytics.
  - Saved at
    `C:\Users\ShaulRoyzen\Documents\personal\repos\podbean-migration-backup-2026-06-23`.
- [x] Claim the existing Spotify show.
  - `https://open.spotify.com/show/4L5uYe7yGitsip9lnh44yL`
- [x] Enable Podbean's ownership verification email for Spotify.
- [x] Submit the existing Apple Podcasts show ownership claim.
  - Submitted and completed June 23, 2026.
- [x] Use Apple's existing-show claim flow; no duplicate new show was
  submitted.
- [x] Confirm the existing show appears in Apple Podcasts Connect.
- [x] Confirm its settings are accessible.
- [x] Keep Podbean's **Redirect to a New Feed** field empty during Stage 2.

## Remaining during Stage 2

### Directory inventory and recovery

- [ ] Complete [DIRECTORY_INVENTORY.md](DIRECTORY_INVENTORY.md) with every
  existing public listing URL.
- [ ] Record the account owner or email without recording passwords.
- [ ] Verify password recovery or two-factor authentication for Podbean,
  Spotify, and Apple.
- [ ] Keep Podbean's ownership-verification email and Apple verification
  settings enabled through cutover.

### Real new-episode test

Wait for a genuinely new YouTube episode during the soak. After the automated
sync succeeds:

- [ ] Confirm the episode appears in the canonical feed.
- [ ] Play it from the beginning in a podcast application.
- [ ] Seek to the middle and confirm playback resumes.
- [ ] Record the episode title and application in [STATUS.md](STATUS.md).

## At the end of the soak

On or after June 30, 2026 at 13:45 Israel time:

- [ ] Open GitHub Actions → **Monitor Migration Soak**.
- [ ] Confirm the latest successful summary reports no failed sync runs and at
  least one new episode. Scheduling-delay warnings are acceptable when every
  run that started succeeded.
- [ ] Download the `migration-soak-status-*` artifact.
- [ ] Open GitHub Actions → **Capture Migration Evidence**.
- [ ] Download the latest `migration-evidence-*` artifact.
- [ ] Store both artifacts with the Podbean analytics export.
- [ ] Mark the Stage 2 evidence in [STATUS.md](STATUS.md).

Do not configure the Podbean redirect until every Stage 2 requirement passes.
