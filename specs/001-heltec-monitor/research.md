# Phase 0 Research: Heltec Environmental Monitor

Every entry below was verified against a current authoritative source
before being used in `plan.md` or code, per Constitution Principle III
("No Invented Hardware Facts"). Verified 2026-09-10.

## Board & toolchain

- **Decision**: PlatformIO, `platform = espressif32`, `board =
  heltec_wifi_kit_32_V3`, `framework = arduino`.
- **Rationale**: This is the official PlatformIO board id for the exact
  board (ESP32-S3FN8, 8MB flash, 240MHz), documented at
  docs.platformio.org/en/latest/boards/espressif32/heltec_wifi_kit_32_V3.html.
  Arduino framework is chosen (over ESP-IDF) because Heltec's own examples
  and the OLED/BME280 libraries below are Arduino-first, which keeps the
  example approachable for a beginner-focused workshop.
- **Alternatives considered**: ESP-IDF directly — rejected for this
  workshop because it adds a steeper learning curve without changing any
  of the product decisions the spec/clarify stages are meant to teach.

## OLED display

- **Decision**: 0.96" 128×64 SSD1306 OLED, I2C address `0x3C`, driven via
  the `SSD1306Wire` class from the ThingPulse `esp8266-oled-ssd1306`
  library (the same class Heltec's own
  `WiFi_Kit_32_V3_FactoryTest.ino` example uses), with pins `SDA_OLED=17`,
  `SCL_OLED=18`, `RST_OLED=21` — **not** the generic ESP32 default I2C
  pins (21/22). Confirmed via the official Heltec factory-test example
  source and the `WiFi_Kit_series` pin definitions.
- **Rationale**: Using the board's actual dedicated OLED pins (rather than
  assuming generic ESP32 I2C defaults) is exactly the kind of
  hardware-specific fact this project's constitution requires verifying —
  and it is a real, documented beginner mistake (see
  `examples/prompt-only/README.md`).
- **Alternatives considered**: U8g2 library — also works with this board
  and is popular in the Heltec community, but `SSD1306Wire` matches
  Heltec's own official example more closely and has a smaller API
  surface for a beginner workshop.

## Power sequencing (Vext)

- **Decision**: `Vext` = GPIO36, **active LOW**. Must be driven LOW to
  power the OLED and any external I2C sensor before use, and can be driven
  HIGH to power them off (e.g., to save battery). Max 350mA on this rail.
- **Rationale**: Confirmed from Heltec's official pin documentation and
  factory-test example (`VextON()`/`VextOFF()` helper functions). Without
  this, the OLED does not power on at all — this is the second real
  beginner mistake baked into `examples/prompt-only/naive_monitor.ino`.

## Sensor

Two sensors are supported, selected at PlatformIO build time (GitHub
issue #2) — this section originally documented BME280 alone and rejected
DHT22 for a first version of this spec; that rejection is superseded
below now that a DHT22 is the sensor actually on hand.

### BME280 (env: `heltec_wifi_kit_32_V3`)

- **Decision**: BME280 (temperature/humidity/pressure), I2C address
  `0x76` (fallback `0x77` if the module's `SDO` pin is pulled high),
  wired to the same I2C bus as the OLED (`SDA_OLED`/`SCL_OLED`), powered
  from the same `Vext` rail. Libraries: `adafruit/Adafruit BME280 Library`
  + `adafruit/Adafruit Unified Sensor` (its required dependency).
- **Rationale**: I2C, so it shares the existing bus/power rail rather
  than needing new wiring for a second protocol; the Adafruit library
  pairing is the standard, actively-maintained way to use it from
  Arduino/PlatformIO.
- **Alternatives considered**: A thermistor on ADC — rejected because it
  needs manual calibration math that would distract from the Spec Kit
  teaching point.

### AM2302/DHT22 (env: `heltec_wifi_kit_32_V3_dht22`, default)

- **Decision**: AM2302 (DHT22), temperature only for this feature (see
  spec.md Assumptions — humidity is a suggested student extension), 3-pin
  module (GND/VCC/DATA) with the pull-up resistor built into the module
  in hand (no external resistor needed). DATA on **GPIO4**. Powered from
  the same `Vext` rail as the OLED. Library: `adafruit/DHT sensor
  library` + `adafruit/Adafruit Unified Sensor` (shared dependency with
  the BME280 env).
- **Rationale for GPIO4**: Verified directly against
  `framework-arduinoespressif32/variants/heltec_wifi_kit_32_V3/pins_arduino.h`
  as installed by this project's PlatformIO toolchain — the actual file
  the build compiles against, not a third-party pinout page (Constitution
  Principle III). That file defines `SDA_OLED=17`, `SCL_OLED=18`,
  `RST_OLED=21`, `Vext=36`, `TX=43`, `RX=44`, `KEY_BUILTIN=0` (boot
  button) as already spoken for. GPIO4 has none of those roles, is not a
  strapping pin (`0`/`3` are, per the ESP32-S3 datasheet), and is not one
  of the native-USB D+/D- pins (`19`/`20`). It is unused anywhere else in
  this firmware.
- **Sampling interval**: the DHT22 datasheet's minimum interval between
  reads is ~2 seconds; reading faster reliably returns stale/failed
  reads. This is why FR-001/FR-006 now specify a 2-second cycle uniformly
  for both sensor envs (spec.md Clarifications, session 2026-09-14),
  rather than a sensor-specific timing branch in `main.cpp`.
- **Failure detection**: the DHT library returns NaN/an error status on a
  checksum or timing failure, the same shape `sensor_adapter`'s existing
  `isnan` check already handles for BME280 — so the existing
  3-consecutive-failure debounce (FR-005) applies unmodified. DHT22 reads
  are more failure-prone under fast polling than I2C in general, which is
  a further reason the 2-second floor matters; the debounce count itself
  does not need to change.
- **Alternatives considered**: none re-evaluated here — DHT22 was not a
  competitive choice against BME280 in the abstract (see the original
  rejection below), it is simply the sensor available for this workshop
  run, and the spec now accommodates either.

### Original BME280-vs-DHT22 comparison (2026-09-10, kept for context)

DHT22 — single-wire, cheaper, but needs a dedicated GPIO and its own
timing-sensitive driver instead of sharing the existing I2C bus; rejected
at the time to keep the wiring/story simpler for a workshop. This is no
longer a rejection, since both are now supported side by side — but the
tradeoff described (extra GPIO, timing sensitivity) is exactly what
sections above had to account for.

## Testing approach

- **Decision**: PlatformIO's built-in `native` platform (compiles and
  runs `test/` on the host machine, no board attached) using Unity
  (PlatformIO's bundled C test framework) for `monitor_logic`.
- **Rationale**: This is what makes Constitution Principle II achievable
  without requiring hardware for every test run — critical both for CI
  and for a live workshop where the physical board is a shared, limited
  resource.
- **Alternatives considered**: On-device tests only — rejected because it
  would make the hysteresis/debounce logic untestable without the exact
  physical board present, contradicting Principle II.
