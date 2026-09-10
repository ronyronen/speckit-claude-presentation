# VS Code Setup

The primary environment demonstrated in this workshop. See
[`textbook.md` Chapter 6](textbook.md#6-development-environment-vs-code)
for the reasoning behind each choice below.

## Open the project

```bash
code speckit-claude-presentation.code-workspace
```

## Recommended extensions

Install only these — each one has a specific job in this workshop, and
nothing was added just to lengthen the list:

| Extension | Marketplace ID | Why |
|---|---|---|
| PlatformIO IDE | `platformio.platformio-ide` | Build/upload/monitor the Heltec firmware from the editor |
| C/C++ | `ms-vscode.cpptools` | IntelliSense across `firmware/src` and `firmware/include` |

Already built in, no install needed: Git integration, the integrated
terminal (where you run `specify`, `pio`, `claude`, `codex`), and Markdown
preview (`Cmd/Ctrl+Shift+V` on a `.md` file).

**Optional, not required for the workshop**: GitLens (richer blame/diff
views while narrating history live) and Error Lens (inline diagnostics).
Skip them if you want the leanest possible setup.

## Using the integrated terminal

Every command in this repository is CLI-first on purpose (see
`textbook.md` Chapter 4) — this keeps the project portable between
editors and between Claude Code and Codex. Open a terminal
(`` Ctrl+` ``) and run any of:

```bash
specify --version
claude          # or: codex
cd firmware && pio test -e native
```

## PlatformIO project

Open `firmware/` as the PlatformIO project root (the PlatformIO extension
detects `firmware/platformio.ini` automatically once you open the
`firmware` folder, or use its "Open Project" picker). The PlatformIO
sidebar gives you Build / Upload / Monitor buttons equivalent to the
`pio` CLI commands in [`setup.md`](setup.md).
