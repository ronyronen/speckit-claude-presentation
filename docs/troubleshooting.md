# Troubleshooting

## Spec Kit / `specify` CLI

**`specify: command not found` after `uv tool install specify-cli`**
Make sure `uv`'s tool bin directory is on your `PATH` (`uv tool update-shell`
or check `~/.local/bin`).

**`specify init --here` refuses to run in a non-empty directory**
Add `--force` to skip the confirmation prompt (this repository used
`specify init --here --force --integration claude`).

**Slash command doesn't exist / wrong syntax**
Check `.specify/integration.json` in your project for the actual
`invoke_separator` your installed version produced. This repository's
Claude Code integration uses `/speckit-specify` (hyphen); some tutorials
show `/speckit.specify` (dot) from older Spec Kit releases. Trust the
files actually installed in your project over a blog post.

**`/speckit-analyze` reports a CRITICAL constitution violation**
This blocks `/speckit-implement` for a reason — a constitution `MUST`
principle is meant to be non-negotiable within the workflow. Fix the
spec/plan/tasks to comply, or explicitly amend the constitution via
`/speckit-constitution` (in its own separate, deliberate step — never
silently, per this project's own constitution Governance section).

## PlatformIO / firmware

**`pio test -e native` links but reports "symbol(s) not found"**
Check `[env:native]` in `firmware/platformio.ini` has
`test_build_src = yes`. Without it, PlatformIO's test runner does not
compile `src/` files into the test binary — only `test/` files — so
`monitor_logic.cpp` never gets linked in. (This happened once during this
project's own implementation; see the git history around checkpoint
`08-implemented`.)

**Board not found / upload fails**
Confirm the Heltec WiFi Kit V3 is connected via a USB-C cable that
supports data (not charge-only), and that no other program (e.g. a
Serial monitor) is holding the port open.

**OLED stays completely blank**
Two board-specific causes, both realistic beginner mistakes (see
[`examples/prompt-only/README.md`](../examples/prompt-only/README.md)):

1. `Vext` (GPIO36) was never pulled LOW before `display.init()` — the
   OLED has no power.
2. The code used the generic ESP32 I2C default pins (21/22) instead of
   this board's dedicated OLED pins (`SDA=17, SCL=18, RST=21`).

**BME280 not detected**
Try both I2C addresses — `0x76` and `0x77` — depending on how the
module's `SDO` pin is strapped. Confirm it shares the same `Vext`-gated
power rail and I2C bus as the OLED (`firmware/README.md`).

## General

**A spec/plan/tasks file seems to contradict another one**
That's exactly what `/speckit-analyze` is for — see
[`textbook.md` Chapter 15](textbook.md#15-analyze) and this project's own
[`analysis-report.md`](../specs/001-heltec-monitor/analysis-report.md)
for a real example it caught.
