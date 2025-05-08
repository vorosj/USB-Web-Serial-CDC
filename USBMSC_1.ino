#ifndef ARDUINO_USB_MODE
#error This ESP32 SoC has no Native USB interface
#elif ARDUINO_USB_MODE == 1
#warning This sketch should be used when USB is in OTG mode
void setup() {}
void loop() {}
#else
#include "USB.h"
#include "USBMSC.h"
#include "index.h"  // A generált index.h, amely a diskImage tömböt tartalmazza

#include <FastLED.h>

#define LED_PIN 48
#define NUM_LEDS 1

CRGB leds[NUM_LEDS];

int Rl = 0, Gl = 0, Bl = 0;

USBMSC MSC;

// A szektorméret fix 512 bájt, a szektorszám a diskImage méretéből adódik
static const uint16_t DISK_SECTOR_SIZE = 512;
static const uint32_t DISK_SECTOR_COUNT = sizeof(diskImage) / DISK_SECTOR_SIZE;

static int32_t onRead(uint32_t lba, uint32_t offset, void *buffer, uint32_t bufsize) {
  Serial.printf("MSC READ: lba: %lu, offset: %lu, bufsize: %lu\n", lba, offset, bufsize);
  // Olvasás a diskImage tömbből
  memcpy(buffer, diskImage + (lba * DISK_SECTOR_SIZE) + offset, bufsize);
  return bufsize;
}

static int32_t onWrite(uint32_t lba, uint32_t offset, uint8_t *buffer, uint32_t bufsize) {
  // Csak olvasható fájlrendszer, írás nem engedélyezett
  Serial.printf("MSC WRITE ATTEMPT: lba: %lu, offset: %lu, bufsize: %lu\n", lba, offset, bufsize);
  return 0;
}

static bool onStartStop(uint8_t power_condition, bool start, bool load_eject) {
  Serial.printf("MSC START/STOP: power: %u, start: %u, eject: %u\n", power_condition, start, load_eject);
  return true;
}

static void usbEventCallback(void *arg, esp_event_base_t event_base, int32_t event_id, void *event_data) {
  if (event_base == ARDUINO_USB_EVENTS) {
    arduino_usb_event_data_t *data = (arduino_usb_event_data_t *)event_data;
    switch (event_id) {
      case ARDUINO_USB_STARTED_EVENT: Serial.println("USB PLUGGED"); break;
      case ARDUINO_USB_STOPPED_EVENT: Serial.println("USB UNPLUGGED"); break;
      case ARDUINO_USB_SUSPEND_EVENT: Serial.printf("USB SUSPENDED: remote_wakeup_en: %u\n", data->suspend.remote_wakeup_en); break;
      case ARDUINO_USB_RESUME_EVENT: Serial.println("USB RESUMED"); break;
      default: break;
    }
  }
}

void setup() {
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);
  Serial.begin(9600);

  Serial.setDebugOutput(true);

  USB.onEvent(usbEventCallback);
  MSC.vendorID("ESP32");       // max 8 chars
  MSC.productID("USB_MSC");    // max 16 chars
  MSC.productRevision("1.0");  // max 4 chars
  MSC.onStartStop(onStartStop);
  MSC.onRead(onRead);
  MSC.onWrite(onWrite);

  MSC.mediaPresent(true);
  MSC.isWritable(false);  // Csak olvasható fájlrendszer

  MSC.begin(DISK_SECTOR_COUNT, DISK_SECTOR_SIZE);
  USB.begin();
}

void loop() {
  if (Serial.available() > 0) {
    char rec = Serial.read();
    int v = 0;
    if (rec == 'R') {
      Rl = 255;
      v = 1;
    }

    if (rec == 'r') {
      Rl = 0;
      v = 1;
    }

    if (rec == 'G') {
      Gl = 255;
      v = 1;
    }

    if (rec == 'g') {
      Gl = 0;
      v = 1;
    }

    if (rec == 'B') {
      Bl = 255;
      v = 1;
    }

    if (rec == 'b') {
      Bl = 0;
      v = 1;
    }

    if (v == 1) {
      v = 0;
      leds[0] = CRGB(Rl, Gl, Bl);
      FastLED.show();
    }
  }
}

#endif              /* ARDUINO_USB_MODE */