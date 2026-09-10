# Using Spec Kit With Codex

This repository is also set up for Codex CLI, added on top of the
existing Claude Code integration — see
[`textbook.md` Chapter 9](textbook.md#9-using-spec-kit-with-codex) for the
full explanation.

## What's installed

```bash
specify integration install codex
```

installs the same nine skills under
[`.agents/skills/`](../.agents/skills/), a shared convention (not
Codex-specific — several agents read from `.agents/`):

```text
.agents/skills/speckit-constitution/SKILL.md
.agents/skills/speckit-specify/SKILL.md
.agents/skills/speckit-clarify/SKILL.md
.agents/skills/speckit-plan/SKILL.md
.agents/skills/speckit-tasks/SKILL.md
.agents/skills/speckit-analyze/SKILL.md
.agents/skills/speckit-implement/SKILL.md
.agents/skills/speckit-checklist/SKILL.md
.agents/skills/speckit-converge/SKILL.md
```

## Running the workflow

Start Codex in the repository root:

```bash
codex
```

Then, in order, using a **dollar prefix** instead of a slash (this is the
one real syntax difference from Claude Code):

```text
$speckit-constitution
$speckit-specify
$speckit-clarify
$speckit-plan
$speckit-tasks
$speckit-analyze
$speckit-implement
```

## Why this proves portability, not just claims it

Both integrations point at the exact same
[`.specify/templates/`](../.specify/templates/) and
[`.specify/scripts/bash/`](../.specify/scripts/bash/) — run
`specify integration list` in this repository and both `claude` and
`codex` show as installed against the same `specs/` directory. Nothing in
`specs/001-heltec-monitor/` or `firmware/` assumes one specific agent;
either one can pick up this project from where the other left off,
because the durable state lives in files, not in either agent's chat
history.
