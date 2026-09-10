#pragma once

#include <cstdint>

#include <Adafruit_BME280.h>

#include "monitor_logic.h"

namespace hw {

// BME280 on the shared I2C bus with the OLED (SDA_OLED/SCL_OLED).
// Address verified in specs/001-heltec-monitor/research.md.
constexpr uint8_t kBme280PrimaryAddress = 0x76;
constexpr uint8_t kBme280FallbackAddress = 0x77;

class SensorAdapter {
 public:
  // Returns true if the BME280 was found and initialized on either
  // candidate address. Call after hw::vext_on().
  bool begin();

  // Always returns a Reading; valid=false if the I2C transaction failed
  // or begin() was never successful (spec.md FR-005 handles the rest).
  monitor::Reading read();

 private:
  Adafruit_BME280 bme_;
  bool initialized_ = false;
};

}  // namespace hw
