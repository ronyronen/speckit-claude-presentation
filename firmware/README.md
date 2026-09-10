# Firmware: Heltec Environmental Monitor

Implements `specs/001-heltec-monitor/` (spec, plan, tasks) on the Heltec
WiFi Kit V3 (ESP32-S3). See that folder for the full spec and design
rationale; this file only covers build/test/flash mechanics.

## Hardware

- **Board**: Heltec WiFi Kit V3 (ESP32-S3FN8, 8MB flash), USB-C
- **Sensor**: BME280, I2C address `0x76` (fallback `0x77`), wired to the
  same I2C bus as the OLED
- **OLED**: onboard 0.96" 128x64 SSD1306, I2C address `0x3C`
- **I2C pins**: `SDA=GPIO17`, `SCL=GPIO18`, `RST=GPIO21` (the board's
  dedicated OLED pins — **not** the generic ESP32 default 21/22; see
  `docs/textbook.md`)
- **Power**: `Vext=GPIO36`, active LOW, gates power to both the OLED and
  the BME280 (max 350mA combined)

## Build & test

```bash
# Native unit tests for the decision logic -- no board required
pio test -e native

# Build for the actual board -- also requires no board connected
pio run -e heltec_wifi_kit_32_V3

# Flash and observe (board required)
pio run -e heltec_wifi_kit_32_V3 -t upload
pio device monitor -b 115200
```

## Verified build output (checkpoint `08-implemented`)

```text
$ pio test -e native
11 test cases: 11 succeeded

$ pio run -e heltec_wifi_kit_32_V3
RAM:   [=         ]   7.1% (used 23124 bytes from 327680 bytes)
Flash: [=         ]  10.8% (used 362623 bytes from 3342336 bytes)
========================= [SUCCESS] Took 25.32 seconds =========================
```

## Hardware verification (checkpoint `09-hardware-verified`)

_Pending — to be filled in after flashing to the physical board (see
`specs/001-heltec-monitor/quickstart.md` steps 3–5)._

## Source layout

| File | Role |
|---|---|
| `include/monitor_logic.h` | `MonitorState`/`Reading`/`State` types — Constitution Principle I: no hardware includes |
| `src/monitor_logic.cpp` | The pure decision logic (hysteresis, debounce) |
| `src/sensor_adapter.*` | BME280 I2C read, returns a `Reading` |
| `src/display_adapter.*` | SSD1306Wire OLED rendering per state |
| `src/serial_reporter.*` | One line per cycle, `contracts/serial-diagnostic-line.md` |
| `src/power.*` | Vext (GPIO36) power-rail control |
| `src/main.cpp` | Wires the above together in `setup()`/`loop()` |
| `test/test_monitor_logic/` | Native unit tests (`pio test -e native`) |
