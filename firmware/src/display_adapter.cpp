#include "display_adapter.h"

#include <Arduino.h>
#include <cstdio>

namespace hw {

bool DisplayAdapter::begin() {
  // The ThingPulse SSD1306Wire constructor has no reset-pin parameter, so
  // RST_OLED must be pulsed manually before init(), per the Heltec V3
  // community-verified sequence (research.md).
  pinMode(kOledRst, OUTPUT);
  digitalWrite(kOledRst, LOW);
  delay(20);
  digitalWrite(kOledRst, HIGH);

  bool ok = display_.init();
  display_.flipScreenVertically();
  return ok;
}

void DisplayAdapter::render(const monitor::State& state) {
  display_.clear();
  display_.setTextAlignment(TEXT_ALIGN_LEFT);

  display_.setFont(ArialMT_Plain_10);
  switch (state.state) {
    case monitor::MonitorState::OK:
      display_.drawString(0, 0, "OK");
      break;
    case monitor::MonitorState::WARNING:
      display_.drawString(0, 0, "WARNING");
      break;
    case monitor::MonitorState::SENSOR_ERROR:
      display_.drawString(0, 0, "SENSOR ERROR");
      break;
  }

  char value[24];
  if (state.has_last_valid) {
    snprintf(value, sizeof(value), "%.1fC", state.last_valid_temperature_c);
  }

  if (state.state == monitor::MonitorState::SENSOR_ERROR) {
    // FR-009: never present stale data as if it were current.
    if (state.has_last_valid) {
      display_.setFont(ArialMT_Plain_24);
      display_.drawString(0, 16, value);
      display_.setFont(ArialMT_Plain_10);
      display_.drawString(0, 48, "Last (stale)");
    }
    // else: no valid reading has ever occurred -- label alone (FR-009).
  } else {
    display_.setFont(ArialMT_Plain_24);
    display_.drawString(0, 16, value);
  }

  display_.display();
}

}  // namespace hw
