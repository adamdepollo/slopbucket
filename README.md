# ai-resources
My personal set of AI agent resources: agent profiles, their reference files, and plugins

## The Plumber

A senior DevOps subagent that keeps CI cheap on Actions minutes ([spec](https://github.com/adamdepollo/slopbucket/issues/1)).

- `plumber/agents/plumber.md`: the profile.
- `plumber/reference/`: the files it reads when a task needs them (`minutes`, `local-check`, `deps`, `workflow`).

Install by copying them to where the profile looks for them:

```sh
cp plumber/agents/plumber.md ~/.claude/agents/
mkdir -p ~/.claude/plumber && cp plumber/reference/* ~/.claude/plumber/
```
