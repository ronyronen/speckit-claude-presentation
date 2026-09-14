// Native unit tests for monitor_logic (Constitution Principle II).
// Run with: pio test -e native  (no Heltec board required)

#include <unity.h>

#include "monitor_logic.h"

using monitor::MonitorState;
using monitor::Reading;
using monitor::State;

namespace {

State valid(const State& prev, float temperature_c) {
  return monitor::update(prev, Reading{true, temperature_c});
}

State invalid(const State& prev) {
  return monitor::update(prev, Reading{false, 0.0f});
}

}  // namespace

// --- User Story 1: basic OK reading -----------------------------------

void test_first_valid_reading_below_threshold_is_ok() {
  State s;
  s = valid(s, 24.0f);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::OK), static_cast<int>(s.state));
  TEST_ASSERT_TRUE(s.has_last_valid);
  TEST_ASSERT_EQUAL_FLOAT(24.0f, s.last_valid_temperature_c);
}

// --- User Story 2: hysteresis (FR-003, FR-004; spec.md Clarifications) --

void test_warning_triggers_strictly_above_27() {
  State s;
  s = valid(s, 27.1f);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::WARNING), static_cast<int>(s.state));
}

void test_exactly_27_does_not_trigger_warning() {
  State s;
  s = valid(s, 27.0f);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::OK), static_cast<int>(s.state));
}

void test_warning_clears_strictly_below_25() {
  State s;
  s = valid(s, 28.0f);  // enter WARNING
  s = valid(s, 24.9f);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::OK), static_cast<int>(s.state));
}

void test_exactly_25_does_not_clear_warning() {
  State s;
  s = valid(s, 28.0f);  // enter WARNING
  s = valid(s, 25.0f);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::WARNING), static_cast<int>(s.state));
}

void test_no_toggling_anywhere_inside_hysteresis_band() {
  State s;
  s = valid(s, 28.0f);  // enter WARNING
  const float band_samples[] = {26.5f, 25.5f, 26.9f, 25.1f, 26.0f};
  for (float t : band_samples) {
    s = valid(s, t);
    TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::WARNING), static_cast<int>(s.state));
  }
}

// --- User Story 3: sensor failure debounce (FR-005) --------------------

void test_one_or_two_failures_do_not_change_state() {
  State s;
  s = valid(s, 24.0f);
  s = invalid(s);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::OK), static_cast<int>(s.state));
  TEST_ASSERT_EQUAL_FLOAT(24.0f, s.last_valid_temperature_c);

  s = invalid(s);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::OK), static_cast<int>(s.state));
  TEST_ASSERT_EQUAL_FLOAT(24.0f, s.last_valid_temperature_c);
}

void test_third_consecutive_failure_enters_sensor_error() {
  State s;
  s = valid(s, 24.0f);
  s = invalid(s);
  s = invalid(s);
  s = invalid(s);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::SENSOR_ERROR), static_cast<int>(s.state));
  // FR-009: last valid reading must be preserved through SENSOR_ERROR.
  TEST_ASSERT_TRUE(s.has_last_valid);
  TEST_ASSERT_EQUAL_FLOAT(24.0f, s.last_valid_temperature_c);
}

void test_recovery_after_sensor_error_reevaluates_normally() {
  State s;
  s = valid(s, 24.0f);
  s = invalid(s);
  s = invalid(s);
  s = invalid(s);  // now SENSOR_ERROR
  s = valid(s, 31.0f);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::WARNING), static_cast<int>(s.state));
}

void test_no_valid_reading_ever_leaves_has_last_valid_false() {
  State s;
  s = invalid(s);
  s = invalid(s);
  s = invalid(s);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::SENSOR_ERROR), static_cast<int>(s.state));
  TEST_ASSERT_FALSE(s.has_last_valid);
}

// --- analysis-report.md E1: FR-007 never crash / never overflow --------

void test_consecutive_failures_saturate_instead_of_overflowing() {
  State s;
  for (int i = 0; i < 1000; ++i) {
    s = invalid(s);
  }
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::SENSOR_ERROR), static_cast<int>(s.state));
  TEST_ASSERT_EQUAL_UINT8(255, s.consecutive_failures);

  // A valid reading must still recover normally after a long outage.
  s = valid(s, 20.0f);
  TEST_ASSERT_EQUAL(static_cast<int>(MonitorState::OK), static_cast<int>(s.state));
  TEST_ASSERT_EQUAL(0, s.consecutive_failures);
}

int main(int argc, char** argv) {
  UNITY_BEGIN();
  RUN_TEST(test_first_valid_reading_below_threshold_is_ok);
  RUN_TEST(test_warning_triggers_strictly_above_27);
  RUN_TEST(test_exactly_27_does_not_trigger_warning);
  RUN_TEST(test_warning_clears_strictly_below_25);
  RUN_TEST(test_exactly_25_does_not_clear_warning);
  RUN_TEST(test_no_toggling_anywhere_inside_hysteresis_band);
  RUN_TEST(test_one_or_two_failures_do_not_change_state);
  RUN_TEST(test_third_consecutive_failure_enters_sensor_error);
  RUN_TEST(test_recovery_after_sensor_error_reevaluates_normally);
  RUN_TEST(test_no_valid_reading_ever_leaves_has_last_valid_false);
  RUN_TEST(test_consecutive_failures_saturate_instead_of_overflowing);
  return UNITY_END();
}
