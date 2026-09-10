#include "monitor_logic.h"

#include <limits>

namespace monitor {

namespace {

// FR-003/FR-004: strict comparisons, exact 30.0/28.0 hold the prior state.
MonitorState evaluate_temperature(MonitorState prev_state, float temperature_c) {
  if (prev_state == MonitorState::WARNING) {
    if (temperature_c < kWarningOffThresholdC) {
      return MonitorState::OK;
    }
    return MonitorState::WARNING;
  }
  // prev_state is OK, or SENSOR_ERROR recovering with a fresh valid
  // reading (data-model.md: treated exactly like a normal reading).
  if (temperature_c > kWarningOnThresholdC) {
    return MonitorState::WARNING;
  }
  return MonitorState::OK;
}

}  // namespace

State update(const State& prev, const Reading& reading) {
  State next = prev;

  if (reading.valid) {
    next.consecutive_failures = 0;
    next.has_last_valid = true;
    next.last_valid_temperature_c = reading.temperature_c;
    next.state = evaluate_temperature(prev.state, reading.temperature_c);
    return next;
  }

  // FR-005: fewer than kFailureDebounceCount consecutive failures MUST NOT
  // change state or the last valid reading. Saturate rather than overflow
  // so an indefinitely disconnected sensor never wraps consecutive_failures
  // back to a small number (FR-007 / analysis-report.md finding E1).
  if (prev.consecutive_failures < std::numeric_limits<uint8_t>::max()) {
    next.consecutive_failures = prev.consecutive_failures + 1;
  }
  if (next.consecutive_failures >= kFailureDebounceCount) {
    next.state = MonitorState::SENSOR_ERROR;
  }
  return next;
}

}  // namespace monitor
