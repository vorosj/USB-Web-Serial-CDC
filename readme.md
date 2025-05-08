I created an ESP32-S3 program that establishes a USB Web Serial connection with a PC or mobile device. What’s interesting is that the web page is also hosted on the ESP itself, and can be opened directly from there by the PC. When connected via USB, the microcontroller (ESP32-S3) behaves like a USB flash drive, containing a single file: index.html. Opening this file loads a web page that includes a JavaScript script, which can establish a Web Serial connection to the microcontroller via the USB port.

This setup allows data to be displayed on the web page, the microcontroller (uC) to be configured through the controls on the web page, and multiple different web pages to be shown, etc.

My example program runs on an S3 board that has a WS2812 RGB LED connected to pin 48. The web page includes three buttons that can toggle the LEDs. Of course, this is just a simple example and can easily be adapted for any real-world application.

One of the challenges was that the filesystems typically used with the ESP32’s internal flash are not compatible with FATxx, so a PC cannot recognize them. This issue was solved in the Arduino Examples/USB/MSC example by creating a static FAT12 image that behaves like a real file system in memory.

I adapted this approach to include a static image that contains the necessary .html file. The .html file includes the JavaScript that establishes the Web Serial connection.

Here’s how the required index.html with JavaScript is integrated into the code:

First, write the .html file with the JavaScript (I used AI assistance for my example).

Then, I created a Python script that converts index.html to index.img (this image can be tested independently by mounting it as a disk image and opening it).

I then wrote another Python script to convert this image into a header file, which is included in main.c.

This way, any HTML and JavaScript can be embedded as long as it fits in the flash memory.

This solution works on any ESP32 board that supports the USB MSC example by Espressif—except, of course, the RGB LED part, which depends on the specific hardware.

Arduino IDE 2.36

my board: https://www.aliexpress.com/item/1005007564893218.html

select Adafruit Feather ESP32 S3 2MB PSRAM in the ide

USB CDC on board enabled

USB mode: USB OTG(TinyUSB)

