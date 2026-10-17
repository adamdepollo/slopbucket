# Workflow

Write a new workflow or job that starts **cheap**: priced before it exists, and run only when it can catch something.

1. **Price it.** Estimate minutes per run (time each step locally or on a similar job; round each job up to a whole minute, times its runner's multiplier) and runs per month (`gh pr list --state merged --limit 500 --search "merged:>=<date 30 days ago>" --json number --jq length` gives the PR rate). Pick the trigger that catches the failure at the lowest count: per PR, `main` only, nightly, a label, release tags, or by hand. Done when you have minutes per run, runs per month and the trigger, and the job beats moving the check into the local check.
2. **Write it with the defaults** below. Done when each default is applied, or set aside with a reason in a YAML comment.
3. **List every path filter** in the PR body: the filter, what it skips, and the evidence that it skips no build input. Done when each one has its evidence.
4. **Prove it.** `actionlint` passes, if installed. The PR's own run exercises a `pull_request` job. Any other run that bills minutes (a trial tag, a dispatch of a long job) waits for the user's OK. Done when one real run is green, or the PR says which run is still owed and what it costs.
5. **Record** the job in `docs/agents/ci.md`: per-run minutes and a one-line reason. The PR body gives which jobs run and skip on each event, and the minutes per month before and after.

## Defaults

- **Concurrency.** Branch and PR workflows cancel the run a new push supersedes:
  ```yaml
  concurrency:
    group: ${{ github.workflow }}-${{ github.ref }}
    cancel-in-progress: true
  ```
  Release and deploy workflows set `cancel-in-progress: false`, so a half-published release always finishes.
- **Triggers.** A PR's run already tests its merge with `main`, so a `push` to `main` that repeats it is a duplicate. `main` runs only to save the caches PRs restore, behind a `paths:` filter on the files that change the cache key. Add `workflow_dispatch` so anyone can run it by hand.
- **Path filters.** A filter skips a whole run, so it lists the inputs it is sure of (docs, `**.md`) or the inputs that matter. **Build inputs** always trigger: the lockfile, manifests, build scripts (`build.rs`, bundler config), toolchain files, OS-specific source dirs, and the workflow file itself. Evidence: replay the filter over the last 30 merged PRs (`gh pr view <n> --json files`) and name any that would have skipped while touching a build input. A skipped workflow leaves a **required** check pending forever; when the check is required, filter inside the job with `dorny/paths-filter` instead.
- **Runner.** `ubuntu-latest` unless the OS is what the job tests. Windows bills 2x and macOS 10x, and cross-compiling on Linux usually beats both.
- **Timeout.** `timeout-minutes` on every job, about twice its normal run. The 360-minute default is a runaway's bill.
- **Caching.** The toolchain's own cache: `Swatinem/rust-cache`, `actions/setup-node` with `cache: npm`, `actions/cache` keyed on the lockfile for the rest. PRs restore caches saved on their base branch, so something on `main` must save each one, and the cache earns its place only when a warm run beats a cold run by more than the save costs. Unused caches are evicted after 7 days, and the repo holds 10 GB.
- **Pinned actions.** GitHub's own `actions/*` on a major tag (`@v4`). Third-party actions on a full commit SHA with the version in a comment (`@<sha> # v2.7.5`).
- **Permissions.** `permissions: contents: read` at the top; a job that writes (releases, comments) asks for its own scope.

## Composable

When a pattern repeats, extract it:

- Within one repo, a run of steps used by two or more jobs becomes a composite action under `.github/actions/<name>/`.
- Across two or more repos, a whole job becomes a reusable workflow (`on: workflow_call`) in a shared repo, called with `uses: <owner>/<repo>/.github/workflows/<file>@<sha>`. Extraction costs no minutes; the calling job bills as before.
