# Quickstart: Validating the Heltec Environmental Monitor

## Prerequisites

- PlatformIO Core installed (`pio --version`)
- Heltec WiFi Kit V3 connected via USB-C (for hardware checks only)
- One of two sensors, wired per whichever env you're using (see
  `firmware/README.md` for the full pin table):
  - **DHT22/AM2302** (default env, `heltec_wifi_kit_32_V3_dht22`): 3-pin
    module, GND/VCC/DATA, DATA on GPIO4, powered from the `Vext` rail
    (GPIO36) or 3.3V directly. No external pull-up needed if your module
    has one built in.
  - **BME280** (`heltec_wifi_kit_32_V3` env): wired to the same I2C bus as
    the OLED (SDA=GPIO17, SCL=GPIO18), powered from the `Vext` rail
    (GPIO36) or 3.3V directly.

## 1. Run the decision-logic unit tests (no hardware required)

```bash
cd firmware
pio test -e native
```

Expected: all `test_monitor_logic` cases pass, including the hysteresis
band (25.0–27.0°C, no toggling), the 3-failure debounce, and the
strict-comparison edge cases at exactly 27.0°C and exactly 25.0°C
(spec.md Clarifications). This proves FR-003–FR-005 without touching the
board — Constitution Principle II.

## 2. Build the firmware

```bash
cd firmware
pio run                          # default env: heltec_wifi_kit_32_V3_dht22 (DHT22)
pio run -e heltec_wifi_kit_32_V3 # explicit BME280 env
```

Expected: clean build, no errors, for whichever env matches the sensor
you have wired. This alone verifies the toolchain, board id, and library
dependencies are all correct — it does not require the physical board to
be connected.

## 3. Flash and observe (requires hardware)

```bash
cd firmware
pio run -t upload                          # DHT22 (default)
# or: pio run -e heltec_wifi_kit_32_V3 -t upload   # BME280
pio device monitor -b 115200
```

Expected Serial output at room temperature (2-second cadence, both envs):

```text
2000,OK,24.8
4000,OK,24.9
```

Expected OLED: current temperature and "OK".

## 4. Verify the warning threshold and hysteresis (requires hardware)

Warm the sensor (e.g. cup a hand around it) until Serial/OLED show
`WARNING` above 27.0°C. Let it cool slowly and confirm the state **stays**
`WARNING` while passing back through 26°C and 25.5°C, and only returns to
`OK` once it drops below 25.0°C. This is the single most important
hardware check in the whole workshop — see spec.md User Story 2. Behavior
is identical regardless of which sensor env is flashed.

## 5. Verify sensor failure handling (requires hardware)

Briefly disconnect the sensor's data wire (SDA for BME280, DATA/GPIO4 for
DHT22). Expected: after 3 sampling cycles (~6 seconds at the 2-second
cadence) of failed reads, OLED shows "SENSOR ERROR" plus the last valid
reading marked stale, and Serial continues printing `SENSOR_ERROR` lines
with the last known temperature (not `-`, unless this happens before any
reading ever succeeded). Reconnect the wire and confirm the device
returns to `OK`/`WARNING` based on the next valid reading, without
needing a reboot.

## Recording results

This checkpoint corresponds to Git tag `09-hardware-verified`. Record the
actual Serial output observed in step 3–5 in `firmware/README.md` once
verified on the physical board, per the project constitution's
hardware-facing "done" criteria.
