# Implementation Plan: Heltec Environmental Monitor

**Branch**: `001-heltec-monitor` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-heltec-monitor/spec.md`

## Summary

Read temperature from a BME280 sensor once per second, render it and the
current state (OK / WARNING / SENSOR_ERROR) on the onboard OLED, and print
one diagnostic line to Serial per cycle. Warning uses a 2°C hysteresis
band (on above 30.0°C, off below 28.0°C) and sensor failure requires 3
consecutive bad reads before being reported, to avoid flapping. The
decision logic (state machine) is a plain-C++ module with zero Arduino
dependencies so it can be unit tested on the host machine without the
physical board.

## Technical Context

**Language/Version**: C++17 (Arduino core for ESP32-S3)

**Primary Dependencies**: Arduino framework (via PlatformIO
`espressif32` platform), `adafruit/Adafruit BME280 Library`,
`adafruit/Adafruit Unified Sensor`, `ThingPulse/ESP8266 and ESP32 OLED
driver for SSD1306 displays` (provides `SSD1306Wire`, the same library
used in Heltec's own factory-test examples)

**Storage**: N/A (no persistence; all state is in RAM, reset on reboot)

**Testing**: PlatformIO native unit tests (`pio test -e native`, using
Unity, PlatformIO's bundled test framework) for the decision logic;
manual hardware verification for the sensor/display adapters (see
`quickstart.md`)

**Target Platform**: Heltec WiFi Kit V3 (ESP32-S3FN8), plus a `native`
PlatformIO environment (runs on the host machine, no hardware) for the
decision-logic unit tests

**Project Type**: Embedded firmware, single PlatformIO project

**Performance Goals**: 1 Hz sampling/render/report cycle (FR-001, FR-006);
OLED redraw must complete well within the 1 s cycle budget on ESP32-S3

**Constraints**: Must not block/crash on sensor failure (FR-007); OLED +
sensor share one I2C bus and one Vext power rail (GPIO36) — Vext must be
enabled before either device is used, per Heltec's own examples

**Scale/Scope**: Single device, single sensor, single feature. No
networking, no persistence, no multi-device concerns.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Decision Logic Is Hardware-Independent | State machine lives in `firmware/lib/monitor_logic` (or `include/` + `src/monitor_logic.cpp`) with no `<Arduino.h>`/`<Wire.h>` includes | PASS (by construction — see Project Structure) |
| II. Test-First For Decision Logic | Native unit tests planned for every FR-003–FR-005 transition before/alongside implementation | PASS (see `tasks.md`, generated next) |
| III. No Invented Hardware Facts | Board/OLED pins/Vext behavior/library names sourced from PlatformIO board docs and Heltec's official Factory Test example, not assumed | PASS — see `research.md` |
| IV. Every Threshold Decision Is Explicit | 30.0/28.0°C, strict comparisons, 3-failure debounce all traced to spec Clarifications | PASS |
| V. Fail Visibly, Never Silently | SENSOR_ERROR + stale-marked last reading on OLED and Serial; no crash path introduced | PASS (verified by unit tests + hardware checkpoint 09) |

No violations — Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/001-heltec-monitor/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/
│   └── serial-diagnostic-line.md   # The device's only external "interface"
└── tasks.md              # Phase 2 output (/speckit-tasks, not this command)
```

### Source Code (repository root)

```text
firmware/
├── platformio.ini
├── include/
│   └── monitor_logic.h     # MonitorState enum + pure decision-logic API
├── src/
│   ├── main.cpp             # setup()/loop(): wires adapters to monitor_logic
│   ├── monitor_logic.cpp    # Constitution Principle I: no Arduino includes
│   ├── sensor_adapter.cpp   # BME280 I2C access, returns Reading (value or failure)
│   ├── sensor_adapter.h
│   ├── display_adapter.cpp  # SSD1306Wire rendering for OK/WARNING/SENSOR_ERROR
│   ├── display_adapter.h
│   ├── serial_reporter.cpp  # One diagnostic line per cycle (contracts/serial-diagnostic-line.md)
│   └── serial_reporter.h
└── test/
    └── test_monitor_logic/
        └── test_monitor_logic.cpp   # Native unit tests, no hardware required
```

**Structure Decision**: Single PlatformIO project under `firmware/`, split
into one pure-logic module (`monitor_logic`) and three thin hardware
adapters (`sensor_adapter`, `display_adapter`, `serial_reporter`) composed
in `main.cpp`. This directly mirrors the Stage D architecture diagram in
the workshop plan (`Sensor → Sensor Adapter → Application State/Decision
Logic → {OLED, Serial, Tests}`) and is what makes Constitution Principle I
and II possible: `monitor_logic` has no hardware dependency, so
`test/test_monitor_logic` can run in PlatformIO's `native` environment on
this machine, with no board attached.

## Complexity Tracking

Not applicable — no constitution violations.
