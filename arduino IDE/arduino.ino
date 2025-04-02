#include <WiFi.h>
#include <HTTPClient.h>
#include <HTTPUpdate.h>
#include <DHT.h>

// Wi-Fi Credentials
const char* ssid = "TP-Link_470A";
const char* password = "37475390";

// DHT Sensor
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Server Details
const char* server = "http://192.168.0.148:5003";
unsigned long lastUpdateCheck = 0;
const long updateInterval = 30000; // Check every 30 seconds

void connectWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
}

void checkForUpdates() {
  if (millis() - lastUpdateCheck >= updateInterval) {
    Serial.println("Checking for updates...");
    
    HTTPClient http;
    http.begin(String(server) + "/check-update");
    int httpCode = http.GET();

    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      if (payload == "update_available") {
        performUpdate();
      }
    }
    http.end();
    lastUpdateCheck = millis();
  }
}

void performUpdate() {
  Serial.println("Downloading firmware...");
  
  WiFiClient client;
  t_httpUpdate_return ret = httpUpdate.update(client, String(server) + "/firmware.bin");

  switch (ret) {
    case HTTP_UPDATE_FAILED:
      Serial.printf("Update failed: %s\n", httpUpdate.getLastErrorString().c_str());
      break;
    case HTTP_UPDATE_NO_UPDATES:
      Serial.println("No updates available");
      break;
    case HTTP_UPDATE_OK:
      Serial.println("Update successful - Rebooting");
      break;
  }
}

void sendSensorData() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(server) + "/data?temp=" + String(temperature) + "&humidity=" + String(humidity);
    
    http.begin(url);
    int httpCode = http.GET();

    if (httpCode > 0) {
      Serial.println("Data sent: " + String(temperature) + "C, " + String(humidity) + "%");
    } else {
      Serial.println("HTTP Error: " + String(httpCode));
    }
    http.end();
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  connectWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }
  
  sendSensorData();
  checkForUpdates(); // Added OTA check
  delay(2000); // Keep original 2s delay for sensor readings
}