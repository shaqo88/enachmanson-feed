# Stage 4: Redirect Window and Podbean Shutdown

Do not cancel Podbean one week after cutover.

Apple requires the redirect and `itunes:new-feed-url` to remain available for
at least four weeks. The earliest supported Podbean cancellation date is 28
days after cutover, and only after all checks pass.

## Day 7 checkpoint

- [ ] The old feed still returns a permanent 301 to the canonical feed.
- [ ] Spotify and Apple use the canonical feed.
- [ ] Other known directories have migrated or were updated directly.
- [ ] No duplicate show or duplicate episodes are visible.
- [ ] A post-cutover episode reached existing followers automatically.
- [ ] Feed and audio availability have remained stable.

## Day 28 checkpoint

- [ ] The old feed has continuously returned the permanent redirect.
- [ ] The canonical feed and audio have remained available.
- [ ] All directory and playback checks still pass.
- [ ] Final Podbean analytics and account records are exported.
- [ ] Podbean support has confirmed whether the redirect survives downgrade or
  cancellation.

If the redirect would stop after cancellation, retain the lowest suitable
Podbean plan through at least the full four-week window. Extend the plan if any
directory has not completed migration.

## Exit gate

Stage 4 is complete only after the 28-day window and successful final
verification. Record the checkpoints and Podbean decision in
[STATUS.md](STATUS.md).
