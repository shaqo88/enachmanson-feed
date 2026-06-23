# Stage 2: Seven-Day Soak

Run the prepared production system for seven consecutive days before cutover.
Restart the seven-day clock after a material feed-generation or sync fix.

The soak started with successful scheduled
[run 28020592571](https://github.com/shaqo88/enachmanson-feed/actions/runs/28020592571)
on June 23, 2026 at 10:45 UTC (13:45 Israel time). The earliest successful
completion is June 30, 2026 at 10:45 UTC (13:45 Israel time).

## Required evidence

- [ ] Every scheduled sync run that starts succeeds for seven consecutive
  days. GitHub may delay or drop scheduled events during high load; these are
  recorded as warnings and reviewed separately from actual workflow failures.
- [ ] At least one genuinely new episode completes the full path:
  YouTube → MP3 → R2 → RSS.
- [ ] The new episode plays from the canonical feed.
- [ ] The canonical feed remains available throughout the soak.
- [ ] All 79 historical enclosure URLs return successfully.
- [ ] Every enclosure supports ranged playback.
- [ ] The artwork is reachable, square, and between 1400 and 3000 pixels.
- [ ] The feed is valid XML and passes a podcast feed validator.
- [ ] All 79 historical GUIDs remain unchanged and unique.
- [x] The `r2.dev` production warning is recorded as accepted temporary risk.
- [x] A future migration to an R2 custom domain is tracked in
  [FUTURE_WORK.md](FUTURE_WORK.md).

The `Monitor Migration Soak` workflow records run counts, actual failures,
scheduling-delay warnings, and new episodes after every sync and once per hour.
`Validate Published Podcast Feed` also runs hourly as an independent public
feed, artwork, and enclosure health check.

## Preserve before cutover

Store these outside Podbean as well as in the migration records:

- [ ] Final Podbean RSS XML snapshot from the latest `Capture Migration
  Evidence` artifact.
- [ ] Podbean analytics export.
- [ ] URLs for every known podcast listing.
- [ ] Account owner, login-recovery, and billing ownership details for each
  directory.
- [ ] A copy of the final artwork.

See [MANUAL_CHECKLIST.md](MANUAL_CHECKLIST.md) for the remaining account and
playback steps.

## Exit gate

Do not proceed to cutover until every required check has evidence and the
seven-day window has completed without a feed outage.

Record the soak dates, run counts, new episode, and evidence in
[STATUS.md](STATUS.md).
