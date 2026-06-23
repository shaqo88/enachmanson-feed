# Stage 5: Final Acceptance

The migration is complete only when every check passes.

These checkboxes intentionally remain open until the post-cutover and
four-week redirect checks are performed. Passing the same technical checks
during Stage 2 does not complete final acceptance.

## Feed and redirect

- [ ] The old Podbean URL returns a permanent HTTP 301 to the exact canonical
  feed.
- [ ] The canonical feed returns HTTP 200 with an XML content type.
- [ ] Exactly 79 historical GUIDs remain unchanged and unique.
- [ ] The feed contains `itunes:new-feed-url` with the canonical URL.
- [ ] The feed declares an episodic show type and non-explicit content.

## Media and artwork

- [ ] All 79 historical audio URLs return successfully.
- [ ] All audio URLs support ranged playback.
- [ ] Artwork is reachable, square, and 1400–3000 pixels.
- [ ] Artwork has an independent recoverable backup.

## Directories and followers

- [ ] Spotify shows no duplicate podcast or duplicate episodes.
- [ ] Apple Podcasts shows no duplicate podcast or duplicate episodes.
- [ ] Other known directories resolve to the canonical feed.
- [ ] Existing followers receive a post-cutover episode automatically.
- [ ] Oldest and newest episodes play and seek correctly in major applications.

## Reliability windows

- [ ] The seven-day soak completed without feed outages.
- [ ] The four-week redirect period completed without feed outages.
- [ ] Podbean cancellation or downgrade will not prematurely remove a required
  redirect.

## Completion

After all checks pass:

- [ ] Mark Stage 5 complete in [STATUS.md](STATUS.md).
- [ ] Record the Podbean downgrade or cancellation date.
- [ ] Preserve the completed migration evidence with the project records.
