#!/usr/bin/env python3
"""Billed Actions minutes per job over recent runs, as a short table.

Usage: minutes.py [-R owner/repo] [--days 30]
Billed minutes round each job up to a whole minute, times the runner's
multiplier (Linux 1, Windows 2, macOS 10). Public repos are not billed.
"""
import argparse, json, math, statistics, subprocess, sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

MULT = {"linux": 1, "windows": 2, "macos": 10}


def gh(*args):
    return json.loads(subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout)


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def os_of(labels):
    text = " ".join(labels).lower()
    return next((o for o in ("windows", "macos") if o in text), "linux")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-R", "--repo")
    p.add_argument("--days", type=int, default=30)
    a = p.parse_args()
    repo = a.repo or gh("repo", "view", "--json", "nameWithOwner")["nameWithOwner"]
    since = datetime.now(timezone.utc) - timedelta(days=a.days)
    runs = gh("run", "list", "-R", repo, "--limit", "500", "--created", f">={since:%Y-%m-%d}",
              "--json", "databaseId,workflowName")

    def jobs(run):
        data = gh("api", "--paginate", f"repos/{repo}/actions/runs/{run['databaseId']}/jobs?per_page=100")
        return run["workflowName"], data["jobs"]

    stats = defaultdict(list)
    with ThreadPoolExecutor(8) as pool:
        for wf, js in pool.map(jobs, runs):
            for j in js:
                if not (j.get("started_at") and j.get("completed_at")):
                    continue
                mins = (ts(j["completed_at"]) - ts(j["started_at"])).total_seconds() / 60
                if mins <= 0:
                    continue
                o = os_of(j.get("labels") or [])
                stats[(wf, j["name"], o)].append((mins, math.ceil(mins) * MULT[o]))

    rows = sorted(((sum(b for _, b in v), k, v) for k, v in stats.items()), reverse=True)
    total = sum(r[0] for r in rows)
    public = not gh("repo", "view", repo, "--json", "isPrivate")["isPrivate"]
    print(f"{repo}, last {a.days} days, {len(runs)} runs" + (" (public: not billed)" if public else ""))
    print(f"{'billed':>7} {'runs':>5} {'median':>7}  {'os':<7} job")
    for billed, (wf, name, o), v in rows:
        med = statistics.median(m for m, _ in v)
        print(f"{billed:>7} {len(v):>5} {med:>6.1f}m  {o:<7} {wf} / {name}")
    print(f"{total:>7} total billed minutes")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.stderr.strip() or str(e))
