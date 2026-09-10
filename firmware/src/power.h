#pragma once

namespace hw {

// Heltec WiFi Kit V3: Vext gates the 3.3V rail that powers the OLED and
// any external I2C sensor (max 350mA). Active LOW: driving it LOW turns
// the rail ON. Verified against Heltec's official factory-test example
// (VextON()/VextOFF() helpers) -- see specs/001-heltec-monitor/research.md.
constexpr int kVextPin = 36;

void vext_on();
void vext_off();

}  // namespace hw
