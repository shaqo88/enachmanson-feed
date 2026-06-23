# Podbean Migration Overview

## Decision

The migration design is sound, but **do not cancel Podbean yet**.

The most important continuity requirement has been met: all 79 historical
episode GUIDs exactly match between the final Podbean-derived feed and the new
feed. Changing these GUIDs would cause podcast applications to treat existing
episodes as new or duplicate episodes.

Use this URL as the single canonical feed for every podcast directory:

<https://shaqo88.github.io/enachmanson-feed/feed.xml>

`feed-standard.xml` is an unregistered compatibility mirror only. Do not submit
it to Spotify, Apple Podcasts, or any other directory.

## Verified baseline

Baseline reviewed on June 22, 2026 and rechecked locally on June 23, 2026:

| Check | Result |
| --- | --- |
| Historical GUID comparison | 79 of 79 match the final Podbean-derived feed |
| Feed episodes | 79 |
| Unique GUIDs | 79 |
| Unique enclosure URLs | 79 |
| R2 audio referenced by the feed | 934,481,955 bytes (0.87 GiB) |
| Unavailable YouTube inventory entries | 4, intentionally excluded from the feed |

The feed was rebuilt on June 23, 2026 at 06:30:15 UTC and still contained 79
items with 79 unique GUIDs.

## Current blockers

- The required seven consecutive days of successful scheduled runs have not
  yet been demonstrated.
- At least one real new episode must complete the full
  YouTube → MP3 → R2 → RSS path during the soak.
- The hardened workflow and new GitHub Pages artwork URL must complete their
  first successful public validation run.
- The audio uses an `r2.dev` public endpoint. Cloudflare documents this
  endpoint as intended for non-production use.
- Apple requires the redirect and `itunes:new-feed-url` to remain available for
  at least four weeks. A shorter shutdown schedule is not supported.

## Migration stages

| Stage | Exit gate |
| --- | --- |
| [1. Repository preparation](01-repository-preparation.md) | Legacy writer removed; feed metadata and workflows hardened |
| [2. Seven-day soak](02-seven-day-soak.md) | Seven days of successful scheduled runs and one real new episode |
| [3. Directory cutover](03-directory-cutover.md) | Podbean 301 and existing directory listings point to the canonical feed |
| [4. Redirect window and shutdown](04-redirect-window-and-shutdown.md) | At least 28 days of stable redirect operation |
| [5. Final acceptance](05-final-acceptance.md) | Every technical and directory-level acceptance test passes |

Record evidence and dates in [STATUS.md](STATUS.md).

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
