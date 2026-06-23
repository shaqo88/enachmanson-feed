#!/usr/bin/env python3
"""Audit the migration soak using GitHub Actions history and repository data."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_REPOSITORY = "shaqo88/enachmanson-feed"
DEFAULT_WORKFLOW = "sync_episodes.yml"
DEFAULT_START = "2026-06-23T10:45:15Z"
DEFAULT_END = "2026-06-30T10:45:15Z"
DEFAULT_BASELINE_REF = "841fe71"
EPISODES_FILE = Path("yt/episodes.json")
MAX_HEALTHY_GAP_HOURS = 2.0

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "enachmanson-feed-soak-monitor",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_runs(repository: str, workflow: str) -> list[dict]:
    runs = []
    for page in range(1, 11):
        response = requests.get(
            f"https://api.github.com/repos/{repository}/actions/workflows/{workflow}/runs",
            headers=github_headers(),
            params={"per_page": 100, "page": page},
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json()["workflow_runs"]
        runs.extend(batch)
        if len(batch) < 100:
            break
    return runs


def load_available_episodes(path: Path) -> dict[str, dict]:
    episodes = json.loads(path.read_text(encoding="utf-8"))
    return {
        episode_id: episode
        for episode_id, episode in episodes.items()
        if not episode.get("unavailable")
    }


def load_baseline_episodes(reference: str) -> dict[str, dict]:
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{reference}:yt/episodes.json"],
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"Could not read baseline episodes from {reference}") from exc
    episodes = json.loads(raw)
    return {
        episode_id: episode
        for episode_id, episode in episodes.items()
        if not episode.get("unavailable")
    }


def audit(
    runs: list[dict],
    start: datetime,
    end: datetime,
    baseline: dict[str, dict],
    current: dict[str, dict],
) -> dict:
    now = datetime.now(timezone.utc)
    scheduled = [
        run
        for run in runs
        if run["event"] == "schedule"
        and run.get("run_started_at")
        and start <= parse_time(run["run_started_at"]) <= end
    ]
    scheduled.sort(key=lambda run: parse_time(run["run_started_at"]))

    completed = [run for run in scheduled if run["status"] == "completed"]
    successful = [run for run in completed if run["conclusion"] == "success"]
    failed = [run for run in completed if run["conclusion"] != "success"]
    pending = [run for run in scheduled if run["status"] != "completed"]

    points = [start] + [parse_time(run["run_started_at"]) for run in scheduled]
    observation_end = min(now, end)
    points.append(observation_end)
    gaps = [
        {
            "start": iso_time(left),
            "end": iso_time(right),
            "hours": round((right - left).total_seconds() / 3600, 2),
        }
        for left, right in zip(points, points[1:])
        if right > left
    ]
    max_gap = max((gap["hours"] for gap in gaps), default=0.0)

    elapsed_hours = max(0.0, (observation_end - start).total_seconds() / 3600)
    expected_to_date = min(168, int(elapsed_hours) + 1)
    new_ids = sorted(set(current) - set(baseline))
    new_episodes = [
        {
            "id": episode_id,
            "title": current[episode_id].get("title", ""),
            "url": current[episode_id].get("url", ""),
        }
        for episode_id in new_ids
    ]

    unhealthy_reasons = []
    if failed:
        unhealthy_reasons.append(f"{len(failed)} scheduled run(s) failed")
    if max_gap > MAX_HEALTHY_GAP_HOURS:
        unhealthy_reasons.append(
            f"largest observed scheduling gap is {max_gap:.2f} hours"
        )

    complete = now >= end
    acceptance_ready = (
        complete
        and not unhealthy_reasons
        and not pending
        and bool(new_episodes)
    )

    return {
        "generated_at": iso_time(now),
        "soak_start": iso_time(start),
        "soak_end": iso_time(end),
        "complete": complete,
        "acceptance_ready": acceptance_ready,
        "expected_runs_to_date": expected_to_date,
        "scheduled_runs": len(scheduled),
        "successful_runs": len(successful),
        "failed_runs": len(failed),
        "pending_runs": len(pending),
        "largest_gap_hours": max_gap,
        "unhealthy_reasons": unhealthy_reasons,
        "new_episodes": new_episodes,
        "runs": [
            {
                "run_number": run["run_number"],
                "status": run["status"],
                "conclusion": run["conclusion"],
                "started_at": run["run_started_at"],
                "url": run["html_url"],
            }
            for run in scheduled
        ],
    }


def markdown_summary(report: dict) -> str:
    state = "ready" if report["acceptance_ready"] else "in progress"
    lines = [
        "# Podcast migration soak",
        "",
        f"- Status: **{state}**",
        f"- Window: `{report['soak_start']}` to `{report['soak_end']}`",
        f"- Expected runs to date: {report['expected_runs_to_date']}",
        f"- Observed scheduled runs: {report['scheduled_runs']}",
        f"- Successful: {report['successful_runs']}",
        f"- Failed: {report['failed_runs']}",
        f"- Pending: {report['pending_runs']}",
        f"- Largest observed gap: {report['largest_gap_hours']:.2f} hours",
        f"- New episodes since baseline: {len(report['new_episodes'])}",
        "",
    ]
    if report["unhealthy_reasons"]:
        lines.extend(["## Health problems", ""])
        lines.extend(f"- {reason}" for reason in report["unhealthy_reasons"])
        lines.append("")
    if report["new_episodes"]:
        lines.extend(["## New episodes", ""])
        lines.extend(
            f"- `{episode['id']}` — {episode['title']}"
            for episode in report["new_episodes"]
        )
        lines.append("")
    lines.extend(["## Scheduled runs", ""])
    lines.extend(
        f"- [Run {run['run_number']}]({run['url']}): "
        f"{run['status']} / {run['conclusion']} at `{run['started_at']}`"
        for run in report["runs"]
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--workflow", default=DEFAULT_WORKFLOW)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--baseline-ref", default=DEFAULT_BASELINE_REF)
    parser.add_argument("--json-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--fail-on-unhealthy", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    try:
        report = audit(
            fetch_runs(args.repository, args.workflow),
            parse_time(args.start),
            parse_time(args.end),
            load_baseline_episodes(args.baseline_ref),
            load_available_episodes(EPISODES_FILE),
        )
    except (OSError, ValueError, RuntimeError, requests.RequestException) as exc:
        print(f"❌ Soak audit failed: {exc}", file=sys.stderr)
        return 1

    summary = markdown_summary(report)
    print(summary)
    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.summary_output:
        Path(args.summary_output).write_text(summary, encoding="utf-8")

    if args.fail_on_unhealthy and report["unhealthy_reasons"]:
        return 1
    if args.require_complete and not report["acceptance_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
