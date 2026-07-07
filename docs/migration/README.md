# Podbean Migration Overview

## Decision

This migration is complete and this repository is retired. The PodBean account
was deleted after Apple Podcasts, Spotify, and Amazon Music were confirmed on
the Torah Pod feed.

Use this URL as the canonical active feed:

<https://torah-pod.pages.dev/nachmanson/feed.xml>

The old GitHub Pages feed remains only as a historical migration pointer:

<https://shaqo88.github.io/enachmanson-feed/feed.xml>

The most important continuity requirement was met during migration: all 79
historical episode GUIDs exactly matched between the final Podbean-derived feed
and the replacement feed. Changing these GUIDs would cause podcast applications
to treat existing episodes as new or duplicate episodes.

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

At retirement, the legacy feed contained 79 items with 79 unique GUIDs. Active
public validation moved to `shaqo88/youtube-podcast-feeds`.

## Current status

- Active sync, feed generation, validation, and website deployment moved to
  `shaqo88/youtube-podcast-feeds`.
- PodBean redirect evidence is no longer available because the PodBean account
  was deleted after cutover.
- This repository can remain archived as migration history.

## Migration stages

| Stage | Exit gate |
| --- | --- |
| [1. Repository preparation](01-repository-preparation.md) | Legacy writer removed; feed metadata and workflows hardened |
| [2. Seven-day soak](02-seven-day-soak.md) | Seven days without actual sync/public-validation failures and one real new episode |
| [3. Directory cutover](03-directory-cutover.md) | Major podcast directories point to the Torah Pod feed |
| [4. Redirect window and shutdown](04-redirect-window-and-shutdown.md) | Waived after major-platform migration and PodBean deletion |
| [5. Final acceptance](05-final-acceptance.md) | Accepted for the platforms used by this project |

Recorded evidence and dates are in [STATUS.md](STATUS.md).

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
