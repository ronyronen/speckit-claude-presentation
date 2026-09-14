# Phase 1 Data Model: Heltec Environmental Monitor

## Reading

A single sensor sample attempt. Unchanged by the BME280/DHT22 dual-sensor
support (GitHub issue #2) — both `sensor_adapter_bme280.cpp` and
`sensor_adapter_dht22.cpp` produce this exact same shape, which is
precisely what lets `monitor_logic` stay sensor-agnostic.

| Field | Type | Notes |
|---|---|---|
| `valid` | bool | `true` if the fitted sensor's read succeeded this cycle |
| `temperature_c` | float | Only meaningful when `valid == true` |

## MonitorState

Enum: `OK`, `WARNING`, `SENSOR_ERROR`.

### State fields carried alongside the enum

| Field | Type | Notes |
|---|---|---|
| `state` | MonitorState | Current state |
| `last_valid_temperature_c` | float (optional/has-value flag) | Last successfully read temperature; unset until the first valid reading ever occurs (FR-009) |
| `consecutive_failures` | uint8 | Reset to 0 on any valid read; counts toward the 3-failure debounce (FR-005) |

### State transitions

Given the current `state` and a new `Reading`:

1. **Reading valid** (`valid == true`):
   - `consecutive_failures` → 0
   - `last_valid_temperature_c` → `reading.temperature_c`
   - If `state != WARNING` and `reading.temperature_c > 27.0` → `state = WARNING`
   - Else if `state == WARNING` and `reading.temperature_c < 25.0` → `state = OK`
   - Else if `state == SENSOR_ERROR` → `state = OK` or `WARNING` based on
     the same two rules above, evaluated fresh (a recovering sensor is
     treated exactly like a normal reading, per spec User Story 3,
     Acceptance Scenario 2)
   - Otherwise `state` is unchanged (this is the hysteresis band, FR-004)

2. **Reading invalid** (`valid == false`):
   - `consecutive_failures` += 1
   - If `consecutive_failures >= 3` → `state = SENSOR_ERROR`
   - Otherwise `state` and `last_valid_temperature_c` are both unchanged
     (FR-005 — a 1–2 read glitch is invisible to the rest of the system)

This transition table is the exact contract that
`test/test_monitor_logic/test_monitor_logic.cpp` verifies (see `tasks.md`).

## Relationships

```text
Reading  --(each sampling cycle)-->  MonitorState transition function --> MonitorState
                                                                              |
                                                                              ├──> display_adapter (OLED)
                                                                              └──> serial_reporter (Serial)
```

`MonitorState` is the only entity shared between the pure logic module and
the two hardware adapters — this is intentional (Constitution Principle
I): the adapters read `MonitorState`, they do not participate in deciding
it.
