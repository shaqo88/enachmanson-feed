# Migration Status

Update this file as each gate is completed. Link evidence such as workflow runs,
saved feed snapshots, validator results, screenshots, and analytics exports.

## Overall status

| Field | Value |
| --- | --- |
| Current stage | Stage 2 — seven-day soak in progress |
| Migration owner | |
| Last status update | June 23, 2026 |
| Canonical feed | `https://shaqo88.github.io/enachmanson-feed/feed.xml` |
| Cutover date/time | Not scheduled |
| Earliest Podbean cancellation date | Cutover date + 28 days |

## Stage gates

- [x] Stage 1: Repository preparation complete
- [ ] Stage 2: Seven-day soak complete
- [ ] Stage 3: Directory cutover complete
- [ ] Stage 4: Four-week redirect window complete
- [ ] Stage 5: Final acceptance complete

## Baseline evidence

- [x] 79 historical episode GUIDs match.
- [x] 79 feed items have 79 unique GUIDs.
- [x] 79 unique enclosure URLs are present.
- [x] Available audio totals 934,481,955 bytes (0.87 GiB).
- [x] Four unavailable YouTube entries are excluded from the feed.
- [x] Public validation passed: [GitHub Actions run 28019687498](https://github.com/shaqo88/enachmanson-feed/actions/runs/28019687498)
- [x] Automated soak monitoring active: [run 28023914547](https://github.com/shaqo88/enachmanson-feed/actions/runs/28023914547)
- [x] Automated RSS/artwork evidence capture active: [run 28023914554](https://github.com/shaqo88/enachmanson-feed/actions/runs/28023914554)
- [ ] Final Podbean RSS snapshot saved:
- [x] Podbean analytics export saved outside this repository:
  `C:\Users\ShaulRoyzen\Documents\personal\repos\podbean-migration-backup-2026-06-23`
- [x] Directory listing inventory created: [DIRECTORY_INVENTORY.md](DIRECTORY_INVENTORY.md)
- [x] Amazon Music listing recorded:
  `https://music.amazon.com/podcasts/c845e46a-4f59-4ca1-9894-4cdd26dfca78`
- [x] No public Pocket Casts, Overcast, Castbox, Podcast Index, or TuneIn
  listing was found on June 23, 2026.
- [x] Spotify ownership confirmed for
  `https://open.spotify.com/show/4L5uYe7yGitsip9lnh44yL`
- [x] Apple ownership claim submitted on June 23, 2026.
- [x] Apple ownership claim completed and show settings accessible on
  June 23, 2026.
- [x] Artwork backup saved: `assets/podcast-cover.png` (1400×1400 PNG)

## Soak record

| Field | Value |
| --- | --- |
| Soak start | June 23, 2026 10:45 UTC / 13:45 Israel time |
| Soak end | June 30, 2026 10:45 UTC / 13:45 Israel time |
| Target scheduled events | 168 (GitHub schedule is best-effort) |
| Observed scheduled runs | 2 |
| Successful scheduled runs | 2 |
| Failed scheduled runs | 0 |
| New episode used for end-to-end test | |
| Sync evidence | [Run 8](https://github.com/shaqo88/enachmanson-feed/actions/runs/28020592571), [Run 9](https://github.com/shaqo88/enachmanson-feed/actions/runs/28031038313) |
| Latest monitor | [Successful corrected monitor](https://github.com/shaqo88/enachmanson-feed/actions/runs/28032205322) |
| Latest public validation | [Successful validation](https://github.com/shaqo88/enachmanson-feed/actions/runs/28032206474) |

GitHub Actions may delay or drop scheduled events during high load. The soak
fails on an actual workflow failure or public validation failure; scheduling
gaps are retained as warnings for review.

## Cutover record

| Field | Value |
| --- | --- |
| Operator | |
| Final Podbean feed URL | |
| Podbean redirect enabled at | |
| Verified HTTP status | |
| Verified `Location` header | |
| Spotify confirmed at | |
| Apple confirmed at | |
| Other directory evidence | |

## Post-cutover checkpoints

- [ ] Day 7 checkpoint completed:
- [ ] Day 28 checkpoint completed:
- [ ] Podbean confirmed redirect behavior after downgrade/cancellation:
- [ ] Podbean cancellation or downgrade completed:
