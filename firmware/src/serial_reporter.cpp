#include "serial_reporter.h"

#include <Arduino.h>

namespace hw {

namespace {
const char* state_name(monitor::MonitorState s) {
  switch (s) {
    case monitor::MonitorState::OK:
      return "OK";
    case monitor::MonitorState::WARNING:
      return "WARNING";
    case monitor::MonitorState::SENSOR_ERROR:
      return "SENSOR_ERROR";
  }
  return "UNKNOWN";
}
}  // namespace

// contracts/serial-diagnostic-line.md: "<millis>,<state>,<temperature_or_dash>"
void report(const monitor::State& state) {
  Serial.print(millis());
  Serial.print(',');
  Serial.print(state_name(state.state));
  Serial.print(',');
  if (state.has_last_valid) {
    Serial.println(state.last_valid_temperature_c, 1);
  } else {
    Serial.println('-');
  }
}

}  // namespace hw
