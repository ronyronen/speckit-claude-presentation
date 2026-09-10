#include <Arduino.h>

#include "display_adapter.h"
#include "monitor_logic.h"
#include "power.h"
#include "sensor_adapter.h"
#include "serial_reporter.h"

namespace {
constexpr unsigned long kSampleIntervalMs = 1000;  // FR-001: 1 Hz

hw::SensorAdapter sensor;
hw::DisplayAdapter oled;
monitor::State monitor_state;
unsigned long last_sample_ms = 0;
}  // namespace

void setup() {
  Serial.begin(115200);

  // Both the OLED and the BME280 sit on the Vext-gated rail; it must be
  // enabled before either is initialized (research.md).
  hw::vext_on();
  delay(50);  // let the rail stabilize before I2C traffic

  if (!oled.begin()) {
    Serial.println("OLED init failed");
  }
  if (!sensor.begin()) {
    Serial.println("BME280 not found at 0x76/0x77 -- starting in SENSOR_ERROR");
  }
}

void loop() {
  unsigned long now = millis();
  if (now - last_sample_ms < kSampleIntervalMs) {
    return;
  }
  last_sample_ms = now;

  monitor::Reading reading = sensor.read();
  monitor_state = monitor::update(monitor_state, reading);

  oled.render(monitor_state);
  hw::report(monitor_state);
}
