# JetBrains / CLion Setup

The Spec Kit workflow is repository-based, not editor-based — nothing in
`.specify/`, `specs/`, `.claude/skills/`, or `.agents/skills/` is specific
to VS Code. This workshop demonstrates VS Code live; this page is the
complete secondary path.

## CLion for the firmware

CLion has native support for PlatformIO projects:

- **Open** `firmware/` directly, or install the PlatformIO plugin
  (Settings → Plugins → search "PlatformIO for CLion") for integrated
  Build/Upload/Monitor actions equivalent to the `pio` CLI.
- You get full C++ indexing, navigation, and debugging across
  `firmware/src` and `firmware/include` — the same source files VS Code
  uses, unmodified.
- Build/test the decision logic exactly as documented in
  [`setup.md`](setup.md): `pio test -e native` and
  `pio run -e heltec_wifi_kit_32_V3` work identically from CLion's
  built-in terminal.

## Any JetBrains IDE, for the Spec Kit workflow itself

- Use the built-in terminal to run `specify`, `claude`, or `codex` — same
  commands as [`textbook.md` Chapters 8–9](textbook.md#8-using-spec-kit-with-claude-code).
- Use the built-in Git tool window to review the checkpoint history
  (`View → Tool Windows → Git`).
- Markdown files (`spec.md`, `plan.md`, `tasks.md`, this file) render with
  the built-in Markdown preview.

## What actually differs from VS Code

Only how your coding agent's skill/command files surface inside an
editor-integrated chat panel, if you use one — that's an agent/editor
integration detail, not a Spec Kit detail. The underlying
`specs/001-heltec-monitor/*.md` files, `.specify/scripts/bash/*.sh`, and
firmware source are identical no matter which editor opens them. If your
agent doesn't have a JetBrains plugin, its CLI in the built-in terminal
works exactly the same as in VS Code's integrated terminal.
