// TrackerAP.ino  (ESP8266 as Access Point)
#include <ESP8266WiFi.h>

const char* ssid = "TrackerAP";
const char* password = "trackpass";

void setup() {
  Serial.begin(115200);
  delay(100);

  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.println();
  Serial.println("Tracker AP started");
  Serial.print("SSID: "); Serial.println(ssid);
  Serial.print("IP: "); Serial.println(IP);
  Serial.print("Channel: "); Serial.println(WiFi.channel());
  // Optionally lower or set tx power if needed (ESP8266-specific)
  // wifi_set_max_tx_power(20); // advanced: requires including SDK headers; not required here
}

void loop() {
  // Keep the AP running. Optionally blink LED
  delay(1000);
}
