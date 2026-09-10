#pragma once

#include <cstdint>

#include <SSD1306Wire.h>

#include "monitor_logic.h"

namespace hw {

// Heltec WiFi Kit V3 OLED: dedicated pins, verified in research.md.
// NOT the generic ESP32 I2C default (21/22) -- see docs/textbook.md and
// examples/prompt-only/README.md for why that distinction matters.
constexpr int kOledSda = 17;
constexpr int kOledScl = 18;
constexpr int kOledRst = 21;
constexpr uint8_t kOledAddress = 0x3C;

class DisplayAdapter {
 public:
  // Pulses RST_OLED, then initializes the SSD1306Wire driver. Call after
  // hw::vext_on().
  bool begin();

  // Renders the current MonitorState per spec.md FR-002/FR-009.
  void render(const monitor::State& state);

 private:
  SSD1306Wire display_{kOledAddress, kOledSda, kOledScl};
};

}  // namespace hw
