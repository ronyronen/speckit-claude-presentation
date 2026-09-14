#include "sensor_adapter.h"

#include <math.h>

#include <Adafruit_BME280.h>

namespace hw {

namespace {
// BME280 on the shared I2C bus with the OLED (SDA_OLED/SCL_OLED).
// Address verified in specs/001-heltec-monitor/research.md.
constexpr uint8_t kBme280PrimaryAddress = 0x76;
constexpr uint8_t kBme280FallbackAddress = 0x77;

Adafruit_BME280 bme;
}  // namespace

bool SensorAdapter::begin() {
  initialized_ = bme.begin(kBme280PrimaryAddress) || bme.begin(kBme280FallbackAddress);
  return initialized_;
}

monitor::Reading SensorAdapter::read() {
  if (!initialized_) {
    return monitor::Reading{false, 0.0f};
  }

  float temperature_c = bme.readTemperature();
  // Adafruit_BME280 returns NaN on a failed I2C transaction.
  if (isnan(temperature_c)) {
    return monitor::Reading{false, 0.0f};
  }

  return monitor::Reading{true, temperature_c};
}

}  // namespace hw
