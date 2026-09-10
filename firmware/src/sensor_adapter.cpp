#include "sensor_adapter.h"

#include <math.h>

namespace hw {

bool SensorAdapter::begin() {
  initialized_ = bme_.begin(kBme280PrimaryAddress) || bme_.begin(kBme280FallbackAddress);
  return initialized_;
}

monitor::Reading SensorAdapter::read() {
  if (!initialized_) {
    return monitor::Reading{false, 0.0f};
  }

  float temperature_c = bme_.readTemperature();
  // Adafruit_BME280 returns NaN on a failed I2C transaction.
  if (isnan(temperature_c)) {
    return monitor::Reading{false, 0.0f};
  }

  return monitor::Reading{true, temperature_c};
}

}  // namespace hw
