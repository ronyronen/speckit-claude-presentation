# Feature Specification: Heltec Environmental Monitor

**Feature Branch**: `001-heltec-monitor`

**Created**: 2026-09-10

**Status**: Clarified

## Clarifications

### Session 2026-09-10

- Q: How often should the device sample the sensor? → A: Once per second.
- Q: At exactly the threshold values, which state wins? → A: Strictly
  greater/less. WARNING triggers only when temperature is strictly above
  30.0°C; OK resumes only when strictly below 28.0°C. A reading of exactly
  30.0°C or exactly 28.0°C does not by itself change state.
- Q: Should a single failed sensor read immediately trigger SENSOR_ERROR,
  or require multiple consecutive failures? → A: 3 consecutive failed
  reads are required before entering SENSOR_ERROR, to tolerate a single
  transient I2C glitch without flapping. A failure count below 3 does not
  change MonitorState at all (the prior OK/WARNING state, and the prior
  valid reading, are held as-is).
- Q: What should the OLED show during SENSOR_ERROR? → A: An explicit
  "SENSOR ERROR" label plus the last valid reading, clearly marked as
  stale (e.g. "Last: 26.4C (stale)"), so the device never presents old
  data as if it were current.
- Q: How frequently should Serial print diagnostics? → A: Every sampling
  cycle (same 1-second cadence as the OLED update), one line containing
  the current MonitorState and the current-or-last-valid temperature.
  Decided alongside the sampling interval since both are driven by the
  same cycle; not treated as a separate high-stakes decision.

**Input**: User description: "Build an application for a Heltec WiFi Kit V3 that reads a sensor, shows the value on the display, and shows a warning when the value is too high."

**Hardware context** (verified, not assumed): Heltec WiFi Kit V3 (ESP32-S3),
0.96" 128x64 SSD1306 OLED at I2C address `0x3C`, BME280 environmental
sensor on the same I2C bus, both powered through `Vext` (GPIO36, active
LOW). See `docs/textbook.md` for sourcing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See the current temperature at a glance (Priority: P1)

As someone glancing at the device, I want to see the current temperature
and whether it's normal or a warning, without needing Serial or a laptop.

**Why this priority**: This is the entire reason the device exists. Without
it, nothing else matters.

**Independent Test**: Power the device in a room at a stable, moderate
temperature. Confirm the OLED shows a numeric temperature and a state
label ("OK") within a few seconds of boot.

**Acceptance Scenarios**:

1. **Given** the device has just booted and the sensor is working, **When**
   a sampling cycle completes, **Then** the OLED shows the current
   temperature reading and the label "OK".
2. **Given** the device is running normally, **When** the temperature is
   read every cycle, **Then** the OLED value updates every cycle (see
   FR-002 for the exact interval).

---

### User Story 2 - Get warned before it's a problem (Priority: P1)

As someone monitoring an environment (e.g. a room, an enclosure), I want a
clear, unmistakable warning when the temperature gets too high, and I want
that warning to behave predictably rather than flicker.

**Why this priority**: This is the feature that turns "a thermometer" into
"a monitor." Without well-defined warning behavior, the device is not
trustworthy.

**Independent Test**: Warm the sensor above the warning threshold and
confirm the OLED and Serial both switch to a WARNING state; cool it back
down and confirm the state clears at the defined lower threshold, not the
same value.

**Acceptance Scenarios**:

1. **Given** the device is in the OK state, **When** the temperature rises
   above 30°C, **Then** the device enters the WARNING state on the OLED and
   Serial.
2. **Given** the device is in the WARNING state, **When** the temperature
   drops below 28°C, **Then** the device returns to the OK state.
3. **Given** the device is in the WARNING state, **When** the temperature
   is between 28°C and 30°C, **Then** the device remains in the WARNING
   state (this is the hysteresis band — see FR-004).

---

### User Story 3 - Know when the sensor itself has failed (Priority: P2)

As someone relying on this device, I want to be able to tell the
difference between "everything is fine" and "the device can no longer
measure anything," so I don't mistake silence or a frozen value for a
normal reading.

**Why this priority**: A monitor that fails silently is worse than no
monitor, because it creates false confidence.

**Independent Test**: Disconnect the sensor (or otherwise force I2C
communication to fail) and confirm the device visibly and audibly (via
Serial) reports SENSOR_ERROR rather than showing a frozen or fabricated
value as if it were current.

**Acceptance Scenarios**:

1. **Given** the device is running normally, **When** a sensor read fails,
   **Then** the device enters SENSOR_ERROR state and reports it on both the
   OLED and Serial.
2. **Given** the device is in SENSOR_ERROR state, **When** a sensor read
   succeeds again, **Then** the device returns to OK or WARNING based on
   the new reading (see clarification on transient failure tolerance).

---

### Edge Cases

- SENSOR_ERROR displays "SENSOR ERROR" plus the last valid reading marked
  stale (see Clarifications). Before any first valid reading has ever been
  obtained, there is no "last valid reading" to show — the OLED shows
  "SENSOR ERROR" with no temperature value in that case.
- A run of 1–2 consecutive failed reads does not change MonitorState; only
  3 consecutive failures trigger SENSOR_ERROR (see Clarifications).
- Threshold comparisons are strict (`>` and `<`, never `>=`/`<=`); readings
  of exactly 30.0°C or exactly 28.0°C do not by themselves change state
  (see Clarifications).
- Serial prints once per sampling cycle (see Clarifications).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST sample temperature from the sensor once per
  second.
- **FR-002**: The system MUST display the current temperature reading on
  the OLED after every successful sample.
- **FR-003**: The system MUST enter WARNING state when temperature is
  strictly above 30.0°C (not at exactly 30.0°C).
- **FR-004**: The system MUST leave WARNING state only when temperature
  falls strictly below 28.0°C (hysteresis band of 2°C; not at exactly
  28.0°C). The system MUST NOT toggle WARNING state for temperatures in
  the closed range [28.0°C, 30.0°C].
- **FR-005**: The system MUST enter SENSOR_ERROR state only after 3
  consecutive failed sensor reads. Fewer than 3 consecutive failures MUST
  NOT change MonitorState or overwrite the last valid reading.
- **FR-006**: The system MUST print one Serial line per sampling cycle
  (1 Hz) containing the current MonitorState and the current-or-last-valid
  temperature.
- **FR-007**: The system MUST NOT crash, hang, or silently reboot on a
  sensor read failure.
- **FR-008**: The decision logic for FR-003–FR-005 (the state machine)
  MUST be implemented independently of any Arduino/hardware API, so it can
  be exercised by automated tests without hardware (Constitution
  Principle I).
- **FR-009**: While in SENSOR_ERROR, the OLED MUST show an explicit
  "SENSOR ERROR" label plus the last valid reading marked as stale, or (if
  no valid reading has ever been obtained) the label alone.

### Key Entities

- **Reading**: A single sensor sample attempt; either a valid temperature
  value or a failure.
- **MonitorState**: One of `OK`, `WARNING`, `SENSOR_ERROR`. Transitions are
  governed by FR-003–FR-005.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An observer can determine the device's current state (OK /
  WARNING / SENSOR_ERROR) from the OLED alone, without Serial, within one
  sampling interval of a state change.
- **SC-002**: The WARNING state never toggles for temperature readings
  strictly between 28.0°C and 30.0°C — zero toggles, not merely a rate
  limit (proves hysteresis works).
- **SC-003**: 100% of state transitions defined in FR-003–FR-005 are
  covered by a native unit test (Constitution Principle II).
- **SC-004**: A sensor disconnection is visible on the OLED within 3
  sampling intervals (the debounce window defined in FR-005), and the
  device continues running (no crash/hang) indefinitely while
  disconnected.

## Assumptions

- The sensor is a BME280 environmental sensor (temperature, humidity,
  pressure) on the shared I2C bus with the OLED — this was a hardware
  choice made explicitly with the project owner before this spec was
  written, not invented by the AI mid-implementation.
- Humidity and pressure are read from the BME280 for future use but are
  out of scope for the warning/state logic in this feature; only
  temperature drives MonitorState.
- Single-device, no networking/WiFi feature is in scope here, even though
  the board has WiFi capability — this monitor is local-only (OLED +
  Serial).
