# Automated Migration Evidence

GitHub Actions stores the evidence files as downloadable artifacts rather than
committing changing snapshots to the repository.

## Daily evidence

The `Capture Migration Evidence` workflow saves:

- the current Podbean RSS feed;
- the current canonical RSS feed;
- the published podcast artwork;
- a GUID continuity report;
- public Apple Podcasts directory search results.

Use the final successful artifact immediately before cutover as the final
Podbean RSS snapshot.

## Soak evidence

The `Monitor Migration Soak` workflow runs after each podcast sync and hourly.
It records:

- expected and observed run counts;
- successful, failed, and pending runs;
- the largest scheduling gap;
- any episodes added after the soak baseline;
- links to every scheduled sync run in the soak window.
