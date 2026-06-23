# Migration Status

Update this file as each gate is completed. Link evidence such as workflow runs,
saved feed snapshots, validator results, screenshots, and analytics exports.

## Overall status

| Field | Value |
| --- | --- |
| Current stage | Stage 1 — awaiting hardened workflow verification |
| Migration owner | |
| Last status update | June 23, 2026 |
| Canonical feed | `https://shaqo88.github.io/enachmanson-feed/feed.xml` |
| Cutover date/time | Not scheduled |
| Earliest Podbean cancellation date | Cutover date + 28 days |

## Stage gates

- [ ] Stage 1: Repository preparation complete
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
- [ ] Final Podbean RSS snapshot saved:
- [ ] Podbean analytics export saved:
- [ ] Directory listing inventory saved:
- [x] Artwork backup saved: `assets/podcast-cover.png` (1400×1400 PNG)

## Soak record

| Field | Value |
| --- | --- |
| Soak start | |
| Soak end | |
| Expected hourly runs | |
| Successful hourly runs | |
| Failed hourly runs | |
| New episode used for end-to-end test | |
| Evidence | |

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
