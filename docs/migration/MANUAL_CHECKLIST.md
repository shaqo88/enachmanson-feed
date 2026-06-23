# Manual Migration Checklist

Automation now covers feed health, all 79 enclosure range checks, artwork,
scheduled-run monitoring, Podbean/canonical RSS snapshots, GUID comparison, and
Apple public-directory discovery.

The remaining work requires authenticated account access or human playback
judgment.

## Do now during Stage 2

### 1. Export Podbean analytics

1. Sign in to Podbean.
2. Open the podcast analytics/statistics area.
3. Select the widest available lifetime date range.
4. Export every available CSV or report.
5. Save the files outside Podbean in a backed-up folder.
6. Add the storage location to [STATUS.md](STATUS.md).

### 2. Complete the directory inventory

1. Open [DIRECTORY_INVENTORY.md](DIRECTORY_INVENTORY.md).
2. For each directory where the show already exists, paste the existing public
   listing URL.
3. Record the account owner or email without recording passwords.
4. Verify that password recovery or two-factor authentication reaches the
   correct owner.
5. Do not create any new show listing.

### 3. Confirm the real new-episode test

Wait for the rabbi to publish a genuinely new YouTube episode during the soak.
After the automated sync succeeds:

1. Open the canonical feed in one podcast application.
2. Confirm the new episode appears.
3. Play from the beginning.
4. Seek to the middle and confirm playback resumes.
5. Record the episode title and application in [STATUS.md](STATUS.md).

## Do at the end of the soak

On or after June 30, 2026 at 13:45 Israel time:

1. Open GitHub Actions → **Monitor Migration Soak**.
2. Open the latest successful run and confirm the summary reports:
   no failed runs, no unhealthy scheduling gap, and at least one new episode.
3. Download its `migration-soak-status-*` artifact.
4. Open GitHub Actions → **Capture Migration Evidence**.
5. Download the latest successful `migration-evidence-*` artifact.
6. Store both artifacts with the Podbean analytics export.
7. Mark the Stage 2 evidence in [STATUS.md](STATUS.md).

Do not configure the Podbean redirect until all Stage 2 checks pass.
