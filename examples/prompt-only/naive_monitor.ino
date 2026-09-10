// Generated from the vague prompt in vague_prompt.md, with no follow-up
// questions and no Spec Kit workflow. Left exactly as first produced.
//
// This file is intentionally NOT built or tested as part of this repository.
// It exists to show what a direct prompt-to-code request actually produces,
// and how many product decisions it silently invents. See README.md in this
// folder for the full list of hidden assumptions and the bugs they cause.

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define WARNING_THRESHOLD 30 // "too high" -- guessed, never confirmed

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Uses the generic ESP32 I2C default pins. Nobody told this code that the
  // Heltec WiFi Kit V3 OLED is wired to GPIO17/18, or that GPIO36 (Vext)
  // must be pulled low first to power the display at all.
  Wire.begin(21, 22);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("Display init failed");
  }
  display.clearDisplay();
}

void loop() {
  float value = dht.readTemperature();

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

  if (isnan(value)) {
    // What should actually happen here was never specified.
    display.println("Sensor error");
  } else {
    display.print("Value: ");
    display.println(value);

    if (value > WARNING_THRESHOLD) {
      display.println("WARNING");
    }
    // No "else" -- the warning simply stops appearing the instant the
    // value dips 0.1 degree below the threshold, then reappears if it
    // creeps back up. Nobody decided whether that's acceptable.
  }

  display.display();
  Serial.println(value);

  delay(1000); // sampling interval also guessed
}
