# Deps

Upgrades, audit warnings and deprecations, batched into **one PR per toolchain** (cargo, npm, Actions, …), each with the local check green.

1. **Survey** each toolchain the repo uses: what is behind and what is flagged.
   - cargo: `cargo update --dry-run --verbose`, `cargo info <crate>` for the latest version of each direct dependency, and `cargo audit` (`cargo install cargo-audit --locked` if missing).
   - npm: `npm outdated` and `npm audit`.
   - Actions: deprecation notices in recent run annotations, and actions pinned to old majors.
   Done when every warning has a line: its crate or package, and which direct dependency pulls it in (`cargo tree --workspace --target all -i <crate>@<ver>` or `npm ls <pkg>`). Plain `cargo tree` resolves only the root package for this host, so it misses workspace members and other OSes.
2. **Question each dependency** before upgrading it: is it used, and is it worth its weight? A flagged crate behind an optional **feature** the repo never exercises goes away by turning the feature off, which beats waiting for upstream. Read the dependency's source to see what the feature gates.
3. **Upgrade** one toolchain per branch, in your own worktree. Keep each PR to its purpose: a change to how updates, signatures or auth work gets its own PR, even when it's available now. Majors only days old, and suites that run only on another machine, go in the PR's "try by hand" list. Where a major changes behaviour the repo can't test here, keep the old behaviour behind its opt-out flag and say when to remove it.
4. **Prove it**: the local check is green, and so is the build for every OS the change touches (cross-check with `cargo xwin check --target x86_64-pc-windows-msvc` for Windows-only code paths). Check that the lockfile diff holds only what you meant.
5. **Open the PR** with a warnings table: each warning, **cleared** or **remains**, and the reason a remaining one stays (build-time only, another OS only, waiting on upstream, a separate PR).
