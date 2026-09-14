# Implementation Plan: Heltec Environmental Monitor

**Branch**: `001-heltec-monitor` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-heltec-monitor/spec.md`

## Summary

Read temperature once every 2 seconds from either of two interchangeable
sensors (BME280 or AM2302/DHT22, selected at build time via PlatformIO
environment — DHT22 is the default), render it and the current state
(OK / WARNING / SENSOR_ERROR) on the onboard OLED, and print one
diagnostic line to Serial per cycle. Warning uses a 2°C hysteresis band
(on above 27.0°C, off below 25.0°C — revised 2026-09-14 during DHT22
hardware bring-up, see spec.md Clarifications) and sensor failure
requires 3
consecutive bad reads before being reported, to avoid flapping. The
decision logic (state machine) is a plain-C++ module with zero Arduino
dependencies so it can be unit tested on the host machine without the
physical board, and is completely unaware of which sensor produced a
given `Reading` (see GitHub issue #2).

## Technical Context

**Language/Version**: C++17 (Arduino core for ESP32-S3)

**Primary Dependencies**: Arduino framework (via PlatformIO
`espressif32` platform); `ThingPulse/ESP8266 and ESP32 OLED driver for
SSD1306 displays` (provides `SSD1306Wire`, the same library used in
Heltec's own factory-test examples) for both envs; per sensor env:
`adafruit/Adafruit BME280 Library` + `adafruit/Adafruit Unified Sensor`
(BME280 env), or `adafruit/DHT sensor library` + `adafruit/Adafruit
Unified Sensor` (DHT22 env, the default)

**Storage**: N/A (no persistence; all state is in RAM, reset on reboot)

**Testing**: PlatformIO native unit tests (`pio test -e native`, using
Unity, PlatformIO's bundled test framework) for the decision logic
(sensor-agnostic — no duplication needed per sensor); manual hardware
verification for the sensor/display adapters, for both sensor envs (see
`quickstart.md`)

**Target Platform**: Heltec WiFi Kit V3 (ESP32-S3FN8) — two board
environments: `heltec_wifi_kit_32_V3` (BME280, unchanged name so existing
tooling like `.vscode/launch.json` keeps working) and the new
`heltec_wifi_kit_32_V3_dht22` (DHT22, set as `default_envs` so a plain
`pio run`/`upload` with no `-e` targets DHT22) — plus a `native`
PlatformIO environment (runs on the host machine, no hardware) for the
decision-logic unit tests

**Project Type**: Embedded firmware, single PlatformIO project

**Performance Goals**: 0.5 Hz (every 2 s) sampling/render/report cycle
(FR-001, FR-006), uniform across both sensor envs — driven by DHT22's
~2 s minimum read interval, not a BME280 constraint; OLED redraw must
complete well within the 2 s cycle budget on ESP32-S3

**Constraints**: Must not block/crash on sensor failure (FR-007); on the
BME280 env, OLED + sensor share one I2C bus and one Vext power rail
(GPIO36); on the DHT22 env, the OLED stays on I2C (GPIO17/18/21) while
the sensor is single-wire on GPIO4, both still Vext-gated — Vext must be
enabled before any device is used, per Heltec's own examples

**Scale/Scope**: Single device, one of two interchangeable sensors
(build-time choice), single feature. No networking, no persistence, no
multi-device concerns.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Check | Result |
|---|---|---|
| I. Decision Logic Is Hardware-Independent | State machine lives in `firmware/lib/monitor_logic` (or `include/` + `src/monitor_logic.cpp`) with no `<Arduino.h>`/`<Wire.h>` includes | PASS (by construction — see Project Structure) |
| II. Test-First For Decision Logic | Native unit tests planned for every FR-003–FR-005 transition before/alongside implementation | PASS (see `tasks.md`, generated next) |
| III. No Invented Hardware Facts | Board/OLED pins/Vext behavior/library names sourced from PlatformIO board docs and Heltec's official Factory Test example, not assumed. DHT22's GPIO4 data pin verified directly against the installed `framework-arduinoespressif32` variant's `pins_arduino.h` for this exact board (the file the build actually compiles against), not a third-party pinout page | PASS — see `research.md` |
| IV. Every Threshold Decision Is Explicit | 27.0/25.0°C (revised 2026-09-14), strict comparisons, 3-failure debounce all traced to spec Clarifications | PASS |
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
├── platformio.ini           # native, heltec_wifi_kit_32_V3 (BME280), heltec_wifi_kit_32_V3_dht22 (default)
├── include/
│   └── monitor_logic.h      # MonitorState enum + pure decision-logic API
├── src/
│   ├── main.cpp                    # setup()/loop(): wires adapters to monitor_logic
│   ├── monitor_logic.cpp           # Constitution Principle I: no Arduino includes
│   ├── sensor_adapter.h            # Shared SensorAdapter interface (begin()/read()) for both sensors
│   ├── sensor_adapter_bme280.cpp   # BME280 I2C access -- compiled only into heltec_wifi_kit_32_V3
│   ├── sensor_adapter_dht22.cpp    # DHT22 GPIO4 access -- compiled only into heltec_wifi_kit_32_V3_dht22
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
this machine, with no board attached. The sensor swap (GitHub issue #2)
extends this by splitting `sensor_adapter.cpp` into two implementations
of the same header-declared interface, each `build_src_filter`-selected
per board env (the same mechanism `native` already uses to select only
`monitor_logic.cpp`) — `main.cpp`, `monitor_logic`, `display_adapter`, and
`serial_reporter` are identical across both board envs.

## Complexity Tracking

Not applicable — no constitution violations.
