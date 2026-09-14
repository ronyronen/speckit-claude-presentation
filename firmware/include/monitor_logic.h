#pragma once

// Constitution Principle I: this header (and monitor_logic.cpp) MUST NOT
// include Arduino.h, Wire.h, or any hardware/library header. That is what
// lets firmware/test/test_monitor_logic run natively on a development
// machine with no Heltec board attached.
#include <cstdint>

namespace monitor {

enum class MonitorState : uint8_t {
  OK,
  WARNING,
  SENSOR_ERROR,
};

// A single sensor sample attempt (spec.md data-model.md "Reading").
struct Reading {
  bool valid;
  float temperature_c;
};

// spec.md Clarifications, 2026-09-10 (thresholds revised 2026-09-14
// during DHT22 hardware bring-up).
constexpr float kWarningOnThresholdC = 27.0f;   // strictly above -> WARNING
constexpr float kWarningOffThresholdC = 25.0f;  // strictly below -> OK
constexpr uint8_t kFailureDebounceCount = 3;    // consecutive failures -> SENSOR_ERROR

// Accumulated monitor state (spec.md data-model.md "MonitorState").
struct State {
  MonitorState state = MonitorState::OK;
  bool has_last_valid = false;
  float last_valid_temperature_c = 0.0f;
  uint8_t consecutive_failures = 0;
};

// Pure transition function: given the previous State and a new Reading,
// returns the next State. See specs/001-heltec-monitor/data-model.md for
// the full transition table this implements.
State update(const State& prev, const Reading& reading);

}  // namespace monitor
