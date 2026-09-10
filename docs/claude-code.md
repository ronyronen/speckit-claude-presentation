# Using Spec Kit With Claude Code

This repository was built using exactly this workflow — see
[`textbook.md` Chapter 8](textbook.md#8-using-spec-kit-with-claude-code)
for the full explanation.

## What's installed

```bash
specify init --here --force --integration claude
```

installs one skill per Spec Kit command under
[`.claude/skills/`](../.claude/skills/):

```text
.claude/skills/speckit-constitution/SKILL.md
.claude/skills/speckit-specify/SKILL.md
.claude/skills/speckit-clarify/SKILL.md
.claude/skills/speckit-plan/SKILL.md
.claude/skills/speckit-tasks/SKILL.md
.claude/skills/speckit-analyze/SKILL.md
.claude/skills/speckit-implement/SKILL.md
.claude/skills/speckit-checklist/SKILL.md
.claude/skills/speckit-converge/SKILL.md
```

## Running the workflow

Start Claude Code in the repository root:

```bash
claude
```

Then, in order:

```text
/speckit-constitution   Establish or update project principles
/speckit-specify        Create the feature spec from a description
/speckit-clarify        Resolve ambiguities (asks up to 5 targeted questions)
/speckit-plan           Generate architecture, research, data model, contracts
/speckit-tasks          Generate the dependency-ordered task list
/speckit-analyze        Read-only cross-check of spec/plan/tasks/constitution
/speckit-implement      Execute tasks.md
```

Note the hyphen: `/speckit-specify`, not `/speckit.specify` — confirmed
by this repository's `.specify/integration.json` (`invoke_separator:
"-"`). Always trust what's actually installed in your project over an
older tutorial.

## Following this project's actual session

Every stage above was run for real to build this repository's
`specs/001-heltec-monitor/` artifacts and `firmware/`. The Git history is
the transcript:

```bash
git log --oneline --all --decorate
```

Each checkpoint tag (`03-spec-created`, `04-spec-clarified`, ...)
corresponds to one Spec Kit command's output — see
[`textbook.md` Chapter 17](textbook.md#git-checkpoints-recap) for the
full list.
