# Tasks: Heltec Environmental Monitor

**Input**: Design documents from `specs/001-heltec-monitor/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — Constitution Principle II requires native unit tests for
every state transition, written alongside the logic they verify.

**Organization**: Tasks are grouped by user story (spec.md) so each story is
independently implementable and testable.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Single PlatformIO project at `firmware/` (see plan.md Project Structure).

---

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Create PlatformIO project skeleton: `firmware/platformio.ini`, `firmware/include/`, `firmware/src/`, `firmware/test/test_monitor_logic/`
- [x] T002 Configure `firmware/platformio.ini` with two environments: `heltec_wifi_kit_32_V3` (platform=espressif32, framework=arduino, lib_deps: adafruit/Adafruit BME280 Library, adafruit/Adafruit Unified Sensor, ThingPulse/ESP8266 and ESP32 OLED driver for SSD1306 displays) and `native` (no lib_deps, for host-only unit tests)

**Checkpoint**: `pio run -e heltec_wifi_kit_32_V3` and `pio test -e native` both execute (even with empty sources) before any logic is written.

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Define `MonitorState` enum (`OK`, `WARNING`, `SENSOR_ERROR`) and `Reading` struct in `firmware/include/monitor_logic.h`, with zero includes of `Arduino.h`/`Wire.h` (Constitution Principle I; data-model.md)
- [x] T004 [P] Implement Vext power helper (`vext_on()`/`vext_off()`, GPIO36 active LOW) in `firmware/src/power.h` / `firmware/src/power.cpp`, used by both the sensor and display adapters (research.md)

**Checkpoint**: Foundation ready — user stories can now proceed.

---

## Phase 3: User Story 1 - See the current temperature at a glance (Priority: P1) 🎯 MVP

**Goal**: OLED shows the current temperature and "OK" within a few seconds of boot, sampling once per second (FR-001, FR-002).

**Independent Test**: Power the device at room temperature; confirm the OLED shows a numeric reading and "OK" within one sampling interval.

### Implementation for User Story 1

- [x] T005 [P] [US1] Implement `sensor_adapter` (`firmware/src/sensor_adapter.h/.cpp`): initializes BME280 at I2C address 0x76 (fallback 0x77) on `SDA_OLED`/`SCL_OLED`, returns a `Reading` (valid + temperature, or invalid) each call
- [x] T006 [P] [US1] Implement `display_adapter` (`firmware/src/display_adapter.h/.cpp`): initializes `SSD1306Wire` on `SDA_OLED=17`, `SCL_OLED=18`, `RST_OLED=21`, address `0x3C`; renders temperature + "OK" for the `OK` state
- [x] T007 [US1] Implement `firmware/src/main.cpp`: `setup()` enables Vext (T004) then initializes sensor_adapter (T005) and display_adapter (T006); `loop()` samples once per second (FR-001) and renders via display_adapter — no state-machine logic yet, straight pass-through
- [ ] T008 [US1] Manual hardware check (quickstart.md step 3): flash and confirm OLED + Serial show a temperature and OK at room temperature

**Checkpoint**: User Story 1 fully functional and independently demonstrable.

---

## Phase 4: User Story 2 - Get warned before it's a problem (Priority: P1)

**Goal**: WARNING state on strictly >27.0°C, clears only on strictly <25.0°C, no toggling inside the [25.0, 27.0] band (FR-003, FR-004; thresholds revised 2026-09-14, see spec.md Clarifications).

**Independent Test**: Warm the sensor above 27.0°C, confirm WARNING; cool below 25.0°C, confirm it clears; hold between 25–27°C, confirm no toggling.

### Tests for User Story 2 ⚠️

> Write these first; they must fail until T009 is implemented.

- [x] T009 [P] [US2] Native unit tests in `firmware/test/test_monitor_logic/test_monitor_logic.cpp`: OK→WARNING at 27.1°C, no transition at exactly 27.0°C, WARNING→OK at 24.9°C, no transition at exactly 25.0°C, no toggling across repeated readings anywhere in [25.0, 27.0] (data-model.md transition table; thresholds revised 2026-09-14)

### Implementation for User Story 2

- [x] T010 [US2] Implement the `OK`/`WARNING` transition logic in `firmware/src/monitor_logic.cpp` (function operating only on `MonitorState`/`Reading`, no hardware includes) until T009 passes
- [x] T011 [US2] Extend `display_adapter` (T006) to render the `WARNING` state distinctly (e.g. inverted/bold text) on the OLED
- [x] T012 [US2] Implement `serial_reporter` (`firmware/src/serial_reporter.h/.cpp`) per `contracts/serial-diagnostic-line.md`, printed once per cycle from `main.cpp`
- [x] T013 [US2] Wire `monitor_logic` (T010) into `main.cpp`'s `loop()`, replacing the pass-through from T007
- [ ] T014 [US2] Manual hardware check (quickstart.md step 4): physically verify the hysteresis band on the real board — this is the checkpoint the whole workshop's teaching point rests on

**Checkpoint**: User Stories 1 AND 2 both work independently; hysteresis is verified in code (T009) and on hardware (T014).

---

## Phase 5: User Story 3 - Know when the sensor itself has failed (Priority: P2)

**Goal**: 3 consecutive failed reads → `SENSOR_ERROR`, shown on OLED with last valid reading marked stale, never silently frozen or crashed (FR-005, FR-007, FR-009).

**Independent Test**: Disconnect the sensor; confirm `SENSOR_ERROR` appears after 3 cycles with the last good reading marked stale; reconnect; confirm automatic recovery to `OK`/`WARNING`.

### Tests for User Story 3 ⚠️

- [x] T015 [P] [US3] Native unit tests in `test_monitor_logic.cpp`: 1–2 consecutive invalid readings do not change `state` or `last_valid_temperature_c`; the 3rd consecutive invalid reading transitions to `SENSOR_ERROR`; a valid reading after `SENSOR_ERROR` re-evaluates `OK`/`WARNING` from that reading (data-model.md)

### Implementation for User Story 3

- [x] T016 [US3] Extend `monitor_logic.cpp` (T010) with `consecutive_failures` tracking and the `SENSOR_ERROR` transition until T015 passes
- [x] T017 [US3] Extend `display_adapter` to render `SENSOR_ERROR`: "SENSOR ERROR" plus last valid reading marked stale, or the label alone if no valid reading has ever occurred (FR-009)
- [x] T018 [US3] Extend `serial_reporter` (T012) to print `-` for temperature only when no valid reading has ever occurred, otherwise the last valid value even while in `SENSOR_ERROR` (contracts/serial-diagnostic-line.md)
- [ ] T019 [US3] Manual hardware check (quickstart.md step 5): physically disconnect/reconnect the sensor and confirm the full failure/recovery cycle

**Checkpoint**: All three user stories independently functional; FR-007 (never crash/hang) confirmed by leaving the sensor disconnected for an extended period during T019.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T020 [P] Write `firmware/README.md`: build/test/flash commands, pin/library summary (cross-links to `docs/textbook.md`)
- [x] T021 Confirm `pio run -e heltec_wifi_kit_32_V3` builds with zero warnings treated as errors (checkpoint `08-implemented`)
- [ ] T022 Run full `quickstart.md` end-to-end on the physical board and record actual Serial/OLED output in `firmware/README.md` (checkpoint `09-hardware-verified`)
- [x] T023 [P] Add a soak test to `test_monitor_logic.cpp`: feed several hundred consecutive invalid `Reading`s and assert `state` stays a valid enum value and `consecutive_failures` never overflows (analysis-report.md finding E1, covers FR-007)
- [x] T024 [P] Add a build-time guard proving `monitor_logic.h`/`.cpp` stay hardware-independent: either a `native`-environment test that compiles them with no Arduino headers on the include path, or a simple grep check in `firmware/README.md`'s verification steps for `Arduino.h`/`Wire.h` (analysis-report.md finding E2, covers FR-008)

---

## Phase 7: Sensor Portability - Support DHT22 alongside BME280 (GitHub issue #2)

**Goal**: Both BME280 and AM2302/DHT22 are supported as interchangeable
temperature sensors, selected at PlatformIO build time; DHT22 becomes the
default env since it's the sensor on hand for this workshop run. No
change to `monitor_logic`, `display_adapter`, or `serial_reporter` — this
phase only touches the sensor adapter, `platformio.ini`, `main.cpp`'s
cadence constant, and docs (spec.md FR-010, FR-001/FR-006 already
amended; see spec.md Clarifications session 2026-09-14).

**Independent Test**: `pio run` with no `-e` builds the DHT22 env and
flashes/runs identically to the existing BME280 behavior (same OLED/
Serial contract, same thresholds/debounce); `pio run -e
heltec_wifi_kit_32_V3` still builds and runs the BME280 path unchanged.

### Implementation for Sensor Portability

- [x] T025 [US1] Rename `firmware/src/sensor_adapter.cpp` to
  `firmware/src/sensor_adapter_bme280.cpp` (no logic change); trim
  `firmware/src/sensor_adapter.h` to the sensor-agnostic `SensorAdapter`
  interface (`begin()`/`read()` returning `monitor::Reading`) shared by
  both implementations, per research.md's revised Sensor section
- [x] T026 [P] [US1] Implement `firmware/src/sensor_adapter_dht22.cpp`:
  DHT22 on **GPIO4** via `adafruit/DHT sensor library`, same
  `SensorAdapter` interface as T025; a failed/checksum read (library
  returns NaN or an error code) maps to `monitor::Reading{false, 0.0f}`,
  feeding the existing 3-consecutive-failure debounce (FR-005) unchanged
- [x] T027 [US1] Update `firmware/platformio.ini`: add
  `default_envs = heltec_wifi_kit_32_V3_dht22`; add the new
  `[env:heltec_wifi_kit_32_V3_dht22]` (lib_deps: `adafruit/DHT sensor
  library`, `adafruit/Adafruit Unified Sensor`; `build_src_filter`
  selecting `sensor_adapter_dht22.cpp` and excluding
  `sensor_adapter_bme280.cpp`); give `[env:heltec_wifi_kit_32_V3]` its own
  `build_src_filter` excluding `sensor_adapter_dht22.cpp` so only one
  adapter ever compiles per env (mirrors the `native` env's existing
  pattern)
- [x] T028 [P] [US1] Update `firmware/src/main.cpp`:
  `kSampleIntervalMs` `1000` → `2000` (FR-001/FR-006, spec.md
  Clarifications session 2026-09-14), update the `// FR-001` comment
- [x] T029 [P] Update `firmware/README.md`: document both sensors, both
  envs, the GPIO4/DHT22 wiring (3-pin, on-board pull-up, Vext-powered),
  and that `heltec_wifi_kit_32_V3_dht22` is now the default `pio run`
  target
- [x] T030 [US1] Manual hardware check (quickstart.md steps 3–5, DHT22
  env): flash the new default env and re-verify temperature display,
  hysteresis, and sensor-failure handling on the DHT22
- [ ] T031 [US1] Manual hardware check (quickstart.md steps 3–5, BME280
  env): re-verify `pio run -e heltec_wifi_kit_32_V3` still behaves
  identically after the T025 rename/split (regression check)
- [x] T032 Record verified Serial/OLED output for the DHT22 env in
  `firmware/README.md` (extends T022's checkpoint); BME280 output still
  pending (see T031)

**Checkpoint**: DHT22 path fully verified on hardware (2026-09-14),
including the revised 27.0°C/25.0°C hysteresis (spec.md FR-010
satisfied for this path). T008/T014/T019/T022 (the original BME280-era
hardware checks) and T031 remain open pending access to BME280 hardware
— functionally superseded on the DHT22 path by T030/T032, but not yet
re-verified on BME280 itself.

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1) → Foundational (Phase 2) → User Stories (Phases 3–5) → Polish (Phase 6) → Sensor Portability (Phase 7)
- Foundational blocks all user stories (T003 defines the shared enum/struct every story extends)
- Phase 7 (DHT22 support, GitHub issue #2) depends on Phase 3 (T005–T007 established the original `sensor_adapter`) but is otherwise independent of Phases 4–6 — it only touches the sensor adapter, build config, and the sampling-interval constant

### User Story Dependencies

- **US1 (P1)**: Depends only on Foundational. No dependency on US2/US3.
- **US2 (P1)**: Depends on Foundational; reuses `display_adapter` from US1 (T006) but its own transition logic (T009–T010) is independently testable via native unit tests without US1's hardware adapters at all.
- **US3 (P2)**: Depends on Foundational; extends the same `monitor_logic.cpp` as US2 (T016 builds on T010) but is independently testable via T015 alone.

### Parallel Opportunities

- T001/T002 (Setup) are sequential (T002 configures what T001 created).
- T004 [P] can run alongside T003.
- T005 and T006 [P] (different files, both only depend on Foundational).
- T009 and T015 are both pure-logic unit tests and can be drafted in parallel with each other, though T015 depends on the `consecutive_failures` field only added in T016 to actually pass — draft first, expect red, then implement.

---

## Implementation Strategy

### MVP First

US1 + US2 together form the minimum viable demo (both P1): a device that
shows temperature and gives a trustworthy, non-flickering warning. US3
(sensor failure) is P2 — valuable, and required by this spec, but the
device is still meaningfully demonstrable after Phase 4 alone.

### Incremental Delivery (matches the workshop's Git checkpoints)

1. Phases 1–2 → firmware builds and tests run, nothing implemented yet
2. Phase 3 (US1) → temperature visible on OLED
3. Phase 4 (US2) → hysteresis warning, verified on hardware
4. Phase 5 (US3) → sensor failure handling, verified on hardware
5. Phase 6 → checkpoints `08-implemented` and `09-hardware-verified`
6. Phase 7 → DHT22 support added alongside BME280 (GitHub issue #2),
   DHT22 becomes the default env, both verified on hardware

## Notes

- Every task in Phases 4–5 that touches `monitor_logic.cpp` must keep it
  free of Arduino/library includes (Constitution Principle I) — this is
  what `/speckit-analyze` and the native test environment both check.
- Commit after each checkpoint, not after each task, to keep the Git
  history readable as a teaching artifact.
