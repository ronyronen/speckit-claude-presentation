# Heltec Environmental Monitor Constitution

## Core Principles

### I. Decision Logic Is Hardware-Independent
Application/decision logic (state transitions, thresholds, hysteresis,
failure handling) MUST live in plain C++ functions/classes that do not
call Arduino, ESP-IDF, or library APIs directly. Sensor reading, OLED
rendering, and Serial output are adapters around this logic, not part of
it. This is what makes the logic unit-testable on a development machine
without hardware.

### II. Test-First For Decision Logic (NON-NEGOTIABLE)
Every state transition and threshold in the spec (normal → warning,
warning → normal, sensor failure entry/exit) MUST have a native unit test
(PlatformIO `test/`, run via `pio test -e native`) written before or
alongside the implementation. A behavior that is only "tested" by staring
at the OLED is not tested.

### III. No Invented Hardware Facts
Sensor models, pin assignments, I2C addresses, power-rail requirements,
and board capabilities MUST be verified against current, authoritative
sources (official Heltec documentation/schematics, PlatformIO board
definitions, official Arduino core headers) before being written into
`spec.md`, `plan.md`, or code. When a fact cannot be verified, it is
recorded as an open question, not guessed.

### IV. Every Threshold Decision Is Explicit
"Too high," "cleared," and "failed" are product decisions, not
implementation details. The spec MUST state exact numeric thresholds,
comparison operators (`>` vs `>=`), hysteresis bands, and debounce/timing
behavior. Code MUST NOT introduce a threshold, comparison, or timing value
that does not trace back to the spec.

### V. Fail Visibly, Never Silently
A sensor read failure MUST be visible on both the OLED and Serial, MUST
preserve (and label) the last known-good reading rather than showing
stale data as if it were current, and MUST NOT crash, hang, or reboot the
device. Recovery behavior (what happens when the sensor starts working
again) MUST be explicitly specified.

## Additional Constraints

- **Target hardware**: Heltec WiFi Kit V3 (ESP32-S3), PlatformIO,
  `framework = arduino`. Toolchain/board/library choices must be verified
  against current PlatformIO and Heltec documentation, not assumed from
  generic ESP32 knowledge (this board's OLED pins are not the ESP32
  default I2C pins — see `docs/textbook.md`).
- **Portability**: Spec Kit artifacts and firmware must remain usable from
  both Claude Code and Codex CLI. Nothing in `specs/`, `firmware/`, or
  `docs/` may assume one specific coding agent.

## Development Workflow

- Firmware changes affecting decision logic require the corresponding
  native unit tests to be updated in the same change.
- A change that touches thresholds, hysteresis, or failure handling must
  update `specs/001-heltec-monitor/spec.md` in the same change — the spec
  and the code are not allowed to drift apart.
- Hardware-facing changes (pins, sensor wiring, power sequencing) are not
  considered done until verified on the physical Heltec WiFi Kit V3.

## Governance

This constitution supersedes ad hoc implementation choices for this
project. Any deviation (e.g., a threshold implemented without a spec
change, or decision logic that reaches into a hardware library) must be
called out explicitly in the pull request/commit description and
justified against these principles, not silently merged.

**Version**: 1.0.0 | **Ratified**: 2026-09-10 | **Last Amended**: 2026-09-10
