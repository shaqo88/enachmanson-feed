name: Recover Episodes from R2

# Manual only — this is a diagnostic/repair tool, never run on a schedule.
on:
  workflow_dispatch:
    inputs:
      rebuild:
        description: 'Write missing entries back into episodes.json (leave unchecked for a safe read-only report)'
        required: false
        type: boolean
        default: false

concurrency:
  group: update-feed
  cancel-in-progress: false

jobs:
  recover:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd  # v6.0.2

      - uses: actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405  # v6.0.2
        with:
          python-version: '3.x'

      - name: Install Deno (JS runtime required by yt-dlp for YouTube n-challenge)
        run: |
          curl -fsSL https://deno.land/install.sh | sh
          echo "$HOME/.deno/bin" >> $GITHUB_PATH

      - name: Install Python dependencies
        run: pip install boto3 "yt-dlp[default]"

      - name: Write YouTube cookies file
        env:
          YOUTUBE_COOKIES: ${{ secrets.YOUTUBE_COOKIES }}
        run: |
          printf '%s' "$YOUTUBE_COOKIES" > /tmp/yt_cookies.txt

      - name: Run recovery script (report mode)
        if: ${{ github.event.inputs.rebuild != 'true' }}
        env:
          R2_ACCOUNT_ID: ${{ secrets.R2_ACCOUNT_ID }}
          R2_ACCESS_KEY: ${{ secrets.R2_ACCESS_KEY }}
          R2_SECRET_KEY: ${{ secrets.R2_SECRET_KEY }}
          R2_BUCKET: ${{ secrets.R2_BUCKET }}
          R2_PUBLIC_URL: ${{ secrets.R2_PUBLIC_URL }}
        run: python3 yt/recover_from_r2.py

      - name: Run recovery script (rebuild mode)
        if: ${{ github.event.inputs.rebuild == 'true' }}
        env:
          R2_ACCOUNT_ID: ${{ secrets.R2_ACCOUNT_ID }}
          R2_ACCESS_KEY: ${{ secrets.R2_ACCESS_KEY }}
          R2_SECRET_KEY: ${{ secrets.R2_SECRET_KEY }}
          R2_BUCKET: ${{ secrets.R2_BUCKET }}
          R2_PUBLIC_URL: ${{ secrets.R2_PUBLIC_URL }}
        run: python3 yt/recover_from_r2.py --rebuild

      - name: Commit recovered episodes.json
        if: ${{ github.event.inputs.rebuild == 'true' }}
        run: |
          git config user.email "actions@github.com"
          git config user.name "GitHub Actions"
          git add yt/episodes.json
          git diff --staged --quiet || git commit -m "🔧 Recover episodes.json from R2 inventory"
          git push
