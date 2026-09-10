# Setup

Quick reference for getting this repository running. For the "why" behind
each tool, see [`textbook.md`](textbook.md).

## Prerequisites

| Tool | Check | Used for |
|---|---|---|
| Git | `git --version` | Version control, checkpoints |
| [uv](https://docs.astral.sh/uv/) | `uv --version` | Installing `specify-cli` |
| [PlatformIO Core](https://platformio.org/install/cli) | `pio --version` | Building/flashing the firmware |
| Claude Code and/or Codex CLI | `claude --version` / `codex --version` | Running the Spec Kit workflow |

## Clone and inspect

```bash
git clone <this-repo-url>
cd speckit-claude-presentation
git log --oneline --all --decorate   # see every workshop checkpoint
```

## Spec Kit (already initialized in this repo)

Already run once for this project (`.specify/`, `.claude/skills/`,
`.agents/skills/` are committed):

```bash
uv tool install specify-cli
specify init --here --force --integration claude
specify integration install codex
```

You do not need to re-run this to use the repository — it's here so you
can see exactly how it was set up, and so you can reproduce it in a new
project of your own.

## Firmware

```bash
cd firmware
pio test -e native                          # decision logic, no board needed
pio run -e heltec_wifi_kit_32_V3             # full build, no board needed
pio run -e heltec_wifi_kit_32_V3 -t upload   # flash (board required)
pio device monitor -b 115200                 # watch Serial output
```

See [`firmware/README.md`](../firmware/README.md) for hardware details
and [`specs/001-heltec-monitor/quickstart.md`](../specs/001-heltec-monitor/quickstart.md)
for the full validation sequence.

## Editor

- [`vscode.md`](vscode.md) — primary, demonstrated in the workshop
- [`jetbrains.md`](jetbrains.md) — secondary path (CLion)

## Agents

- [`claude-code.md`](claude-code.md)
- [`codex.md`](codex.md)

## Something not working?

See [`troubleshooting.md`](troubleshooting.md).
