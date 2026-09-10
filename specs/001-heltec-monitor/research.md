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

- **Decision**: BME280 (temperature/humidity/pressure), I2C address
  `0x76` (fallback `0x77` if the module's `SDO` pin is pulled high),
  wired to the same I2C bus as the OLED (`SDA_OLED`/`SCL_OLED`), powered
  from the same `Vext` rail. Libraries: `adafruit/Adafruit BME280 Library`
  + `adafruit/Adafruit Unified Sensor` (its required dependency).
- **Rationale**: The Heltec WiFi Kit V3 has no onboard environmental
  sensor, so an external one is required (chosen with the project owner
  before this spec was written — see spec.md Assumptions). BME280 is I2C
  (so it can share the existing bus/power rail rather than needing new
  wiring for a second protocol), and the Adafruit library pairing is the
  standard, actively-maintained way to use it from Arduino/PlatformIO.
- **Alternatives considered**: DHT22 — single-wire, cheaper, but needs a
  dedicated GPIO and its own timing-sensitive driver instead of sharing
  the existing I2C bus; rejected to keep the wiring/story simpler for a
  workshop. A thermistor on ADC — rejected because it needs manual
  calibration math that would distract from the Spec Kit teaching point.

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
