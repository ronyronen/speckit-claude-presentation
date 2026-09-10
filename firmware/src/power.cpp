#include "power.h"

#include <Arduino.h>

namespace hw {

void vext_on() {
  pinMode(kVextPin, OUTPUT);
  digitalWrite(kVextPin, LOW);
}

void vext_off() {
  pinMode(kVextPin, OUTPUT);
  digitalWrite(kVextPin, HIGH);
}

}  // namespace hw
