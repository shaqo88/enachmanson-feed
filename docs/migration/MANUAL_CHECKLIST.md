# Manual Migration Checklist

Retired on July 7, 2026. The active feed is now:

<https://torah-pod.pages.dev/nachmanson/feed.xml>

The PodBean account was deleted after Apple Podcasts, Spotify, and Amazon Music
were confirmed on the Torah Pod feed. Remaining unchecked PodBean tasks below
are historical and should not be executed.

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
- [x] Configure the PodBean redirect to the new Torah Pod feed.
- [x] Confirm Apple Podcasts migrated to the new feed.
- [x] Confirm Spotify migrated to the new feed.
- [x] Confirm Amazon Music is managed from a separate email account and is
  configured with the new feed.

## Remaining during Stage 2

### Directory inventory and recovery

- [x] Record the confirmed Spotify, Apple, Amazon Music, and Podbean listings
  in [DIRECTORY_INVENTORY.md](DIRECTORY_INVENTORY.md).
- [x] Search for Pocket Casts, Overcast, Castbox, Podcast Index, and TuneIn.
  No public listings were found on June 23, 2026; recheck after redirect.
- [x] Copy the existing Boomplay, Podchaser, Player FM, and iHeartRadio public
  listing URLs from Podbean into [DIRECTORY_INVENTORY.md](DIRECTORY_INVENTORY.md).
- [x] Claim the existing Amazon Music show.
- [x] Classify Boomplay, Podchaser, Player FM, iHeartRadio, and currently
  undiscovered aggregators as optional post-redirect checks.
- [ ] Record the account owner or email without recording passwords.
- [ ] Verify password recovery or two-factor authentication for the required
  dashboards: Podbean, Spotify, Apple, and Amazon Music.
- [x] Keep Podbean's ownership-verification email and Apple verification
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
- [x] Mark the Stage 2 evidence in [STATUS.md](STATUS.md).

Optional aggregator dashboards do not block Stage 2. Do not configure the
Podbean redirect until every required Stage 2 item passes.

## Historical remaining items after major-platform cutover

- [x] Major platforms were confirmed on the Torah Pod feed.
- [x] PodBean account was deleted after cutover.
- [ ] Historical only: verify the PodBean feed returns HTTP 301 to
  `https://shaqo88.github.io/youtube-podcast-feeds/nachmanson/feed.xml` from a
  network that is not blocked by NetFree.
- [ ] Historical only: keep PodBean redirect active for 28 days from the
  redirect enable date.
- [ ] Historical only: ask PodBean whether the redirect survives
  downgrade/cancellation/deletion.
- [x] PodBean was deleted after the major platforms were confirmed.
- [ ] Historical only: cancel or downgrade PodBean only after the redirect
  window passes and the redirect behavior is understood.
