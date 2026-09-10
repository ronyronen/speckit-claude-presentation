# Stage G — Spec Kit–driven implementation

This is a pointer, not a copy: the actual Spec Kit–driven implementation
lives at [`../../firmware/`](../../firmware/), because it is the one real
firmware project in this repository (there is no value in maintaining a
second copy just to keep it under `examples/`).

Compare it against [`../prompt-only/`](../prompt-only/). The fair way to
read this table is **implicit assumption vs. explicit decision**, not
"wrong vs. right" — see `../prompt-only/README.md` for why hardware
wiring is deliberately *not* one of the rows below (both versions use the
same verified Heltec pins; that fact says nothing about which approach is
better, only that hardware research happened before either was written).

| | Prompt-only | Spec Kit–driven |
|---|---|---|
| Sensor | Guessed (DHT22) — an implicit assumption, since none was specified | Chosen deliberately, documented in `specs/001-heltec-monitor/research.md` |
| Warning threshold | Hardcoded `30`, no reasoning recorded anywhere | `30.0°C` / `28.0°C`, traced to `spec.md` Clarifications |
| Hysteresis | None (flickers at the threshold) | Explicit 2°C band, unit-tested (`test_monitor_logic.cpp`) |
| Sensor failure | Shows "Sensor error", no debounce | 3-failure debounce, last reading preserved and marked stale |
| Testability | None — all logic inline in `loop()` | `monitor_logic` is hardware-independent and natively unit tested |
| Traceability | The prompt in `vague_prompt.md`, nothing else | `spec.md → plan.md → tasks.md → firmware/`, plus `analysis-report.md` catching a real spec inconsistency before implementation |

See [`../../specs/001-heltec-monitor/`](../../specs/001-heltec-monitor/)
for the full spec/plan/tasks/analysis that produced this implementation,
and [`../../firmware/README.md`](../../firmware/README.md) for build/test/
flash instructions.
