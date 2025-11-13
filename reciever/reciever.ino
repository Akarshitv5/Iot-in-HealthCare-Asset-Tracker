// ReceiverScan.ino  (ESP8266 scanning for TrackerAP and printing RSSI)
#include <ESP8266WiFi.h>

const char* targetSSID = "1Plus";
const float txPowerAt1m = -40.0; // assumed Tx power (dBm at 1m) — calibrate for best results
const float pathLossExponent = 2.0; // n: 2 = free space, 2.7-4 for indoors (adjust by environment)

unsigned long lastScan = 0;
const unsigned long scanInterval = 1000; // ms

float rssiToDistance(int rssi, float txPower = txPowerAt1m, float n = pathLossExponent) {
  // distance (m) = 10 ^ ((TxPower - RSSI) / (10 * n))
  float exp = (txPower - (float)rssi) / (10.0 * n);
  return pow(10.0, exp);
}

void setup() {
  Serial.begin(115200);
  delay(100);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(); // ensure clean state
  Serial.println("Receiver ready. Scanning for TrackerAP...");
}

void loop() {
  unsigned long now = millis();
  if (now - lastScan < scanInterval) return;
  lastScan = now;

  int n = WiFi.scanNetworks(false, true); // async=false, hidden=true to include hidden networks
  int foundIndex = -1;
  int foundRSSI = 0;

  for (int i = 0; i < n; ++i) {
    String ss = WiFi.SSID(i);
    if (ss == targetSSID) {
      foundIndex = i;
      foundRSSI = WiFi.RSSI(i);
      break;
    }
  }

  if (foundIndex >= 0) {
    float dist = rssiToDistance(foundRSSI);
    Serial.print(millis());
    Serial.print(",");
    Serial.print("RSSI:");
    Serial.print(foundRSSI);
    Serial.print(",DIST_m:");
    Serial.println(dist, 3);
  } else {
    Serial.print(millis());
    Serial.println(",NOT_FOUND");
  }

  WiFi.scanDelete(); // clear results
}
