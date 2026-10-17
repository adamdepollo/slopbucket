# ai-resources
My personal set of AI agent resources: agent profiles, their reference files, and plugins

## Plugins

This repo is a Claude Code plugin marketplace. Add it once, then install a plugin:

```
/plugin marketplace add adamdepollo/slopbucket
/plugin install plumber@slopbucket
```

- **plumber**: the Plumber, a senior DevOps subagent that keeps CI cheap on Actions minutes ([spec](https://github.com/adamdepollo/slopbucket/issues/1)). `agents/plumber.md` is the profile, and `reference/` holds the files it reads when a task needs them (`minutes`, `local-check`, `deps`, `workflow`).
