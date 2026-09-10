#pragma once

#include "monitor_logic.h"

namespace hw {

// Implements specs/001-heltec-monitor/contracts/serial-diagnostic-line.md
void report(const monitor::State& state);

}  // namespace hw
