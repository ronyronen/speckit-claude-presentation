#include "sensor_adapter.h"

#include <math.h>

#include <DHT.h>

namespace hw {

namespace {
// AM2302 (DHT22), 3-pin module (GND/VCC/DATA), on-board pull-up.
// DATA on GPIO4 -- verified against the installed
// framework-arduinoespressif32 variant's pins_arduino.h for this board
// (see specs/001-heltec-monitor/research.md): free of any OLED/Vext/
// Serial/USB/strapping role.
constexpr uint8_t kDataPin = 4;

DHT dht(kDataPin, DHT22);
}  // namespace

bool SensorAdapter::begin() {
  dht.begin();
  // The DHT library has no bus-presence probe like I2C's begin(); a
  // missing/faulty sensor surfaces as a failed read() instead, which
  // feeds the same 3-consecutive-failure debounce as BME280 (FR-005).
  initialized_ = true;
  return initialized_;
}

monitor::Reading SensorAdapter::read() {
  if (!initialized_) {
    return monitor::Reading{false, 0.0f};
  }

  float temperature_c = dht.readTemperature();
  // The DHT library returns NaN on a failed read (timing/checksum error).
  if (isnan(temperature_c)) {
    return monitor::Reading{false, 0.0f};
  }

  return monitor::Reading{true, temperature_c};
}

}  // namespace hw
