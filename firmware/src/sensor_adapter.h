#pragma once

#include "monitor_logic.h"

namespace hw {

// Shared interface for the fitted temperature sensor, implemented by
// exactly one of sensor_adapter_bme280.cpp / sensor_adapter_dht22.cpp
// per PlatformIO env (see firmware/platformio.ini build_src_filter and
// specs/001-heltec-monitor/research.md). main.cpp is identical
// regardless of which sensor is fitted.
class SensorAdapter {
 public:
  // Returns true if the sensor was found/initialized. Call after
  // hw::vext_on().
  bool begin();

  // Always returns a Reading; valid=false if the read failed or begin()
  // was never successful (spec.md FR-005 handles the rest).
  monitor::Reading read();

 private:
  bool initialized_ = false;
};

}  // namespace hw
