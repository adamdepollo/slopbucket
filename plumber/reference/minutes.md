# Minutes

Measure what each job really costs, then give every job a verdict.

1. **Measure.** Run `~/.claude/plumber/minutes.py -R <owner/repo>` (`--days N` widens the window from 30). It prints billed minutes per job, ranked: each job rounded up to a whole minute, times its runner's multiplier (Linux 1, Windows 2, macOS 10). Rows for jobs gone from `.github/workflows/` are history. A public repo is free: report that and stop. Done when you know which live jobs carry the bill.
2. **Find the waste** in the top jobs. The usual sources:
   - **Duplicate runs**: `gh run list --workflow <file> --json event` shows how many runs re-test on a `push` what the PR's run already tested.
   - **Multiplier**: a Windows or macOS job whose work could run on Linux (cross-compiling, or tests that don't depend on the OS).
   - **Cold caches**: `gh cache list` shows which refs save caches and which keys PRs restore. Every cache a PR restores is saved by some run on `main`, so trace that before cutting a `main` run.
   - **One slow step**: `gh api repos/<owner/repo>/actions/runs/<id>/jobs` gives each step's start and end.
3. **Give a verdict** to every live job over 1 minute:
   - **keep**, with the reason it earns its minutes;
   - **tighten**: the same check for fewer minutes;
   - **move**: to a nightly run, a label, release tags or the local check, naming where;
   - **drop**: proposed in the PR for the user to decide, with what the check covered.
   Done when every such job has one.
4. **Record** each verdict as a one-line reason in the repo's `docs/agents/ci.md`, alongside accepted costs, checks moved and where they went, and known flaky tests.
5. **Change** the tighten and move verdicts, each priced the same way, so anything a fix adds (a scheduled run, a warm-up job) pays for itself in measured minutes. Open them as a PR from your own worktree. The PR body carries the measured table as *before*, the estimated *after* with its arithmetic, and which jobs run or skip on each event.
