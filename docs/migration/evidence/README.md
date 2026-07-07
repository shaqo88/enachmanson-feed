# Automated Migration Evidence

This evidence workflow was retired on July 7, 2026 after the PodBean account
was deleted and the active Nachmanson podcast moved to Torah Pod:

<https://torah-pod.pages.dev/nachmanson/feed.xml>

GitHub Actions stores the evidence files as downloadable artifacts rather than
committing changing snapshots to the repository.

## Daily evidence

The removed `Capture Migration Evidence` workflow saved:

- the current Podbean RSS feed;
- the current canonical RSS feed;
- the published podcast artwork;
- a GUID continuity report;
- public Apple Podcasts directory search results.

Use the final successful artifact before cutover, if available, as the final
Podbean RSS snapshot. Do not re-enable this workflow unless a new PodBean
migration is intentionally created.

## Soak evidence

The `Monitor Migration Soak` workflow runs after each podcast sync and hourly.
It records:

- expected and observed run counts;
- successful, failed, and pending runs;
- the largest scheduling gap, reported as a warning rather than a podcast
  failure when all runs that started succeeded;
- any episodes added after the soak baseline;
- links to every scheduled sync run in the soak window.
