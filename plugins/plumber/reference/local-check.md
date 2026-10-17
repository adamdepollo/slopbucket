# Local check

Give the repo one command that answers **red or green**: the checks that left the runners, plus CI's own, so a PR's CI run confirms rather than discovers.

1. **Find the checks.** Read the CI workflows, the build config's scripts, and the agent docs or handoff notes for checks agents already run by hand. Any existing local command is the one to extend. Done when every check has a line: run in the command, or left to CI or a by-hand run with a reason.
2. **Write the command** in the repo's own idiom (`npm run verify`, `scripts/check`, a `make` target). Its shape:
   - Run each step with its output captured to a log, and stop at the first failure.
   - **Green:** one line, `check: ok (N steps, Ts)`, exit 0.
   - **Red:** `check: FAILED at <step> (<command>)`, then an excerpt of up to ~16 lines, then the full log's path, exit 1. Grep the log for the lines that say what broke (compiler errors, panics, assertion messages, diff hunks), and fall back to its tail.
   - Colour off (`NO_COLOR=1`, `CARGO_TERM_COLOR=never`, the tool's own flag), so excerpts stay readable in a transcript.
3. **Prove it** in a fresh worktree. It passes on a clean checkout. Break it once per tool family (a failing test, a type error, a lint, a format slip), and each one fails with an excerpt that names the cause. Done when every break shows the cause within its excerpt.
4. **Add the rule** as one line near the top of the repo's agent docs (`CLAUDE.md` or `AGENTS.md`): run the command until it prints ok before opening or updating a PR, and say in the PR body that it passed.
5. **Record** in `docs/agents/ci.md` which checks the command runs that CI doesn't, and what is still run by hand.
