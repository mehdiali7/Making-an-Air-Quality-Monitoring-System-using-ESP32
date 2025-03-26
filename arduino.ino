#include <WiFi.h>
#include <DHT.h>
#include <HTTPClient.h>  // Include HTTPClient library

// Wi-Fi Credentials
const char* ssid = "TP-Link_470A";      // Your Wi-Fi name
const char* password = "37475390";         // Your Wi-Fi password

// DHT Sensor Setup
#define DHTPIN 4    // Pin connected to DHT11
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Server Details (Replace with your computer's IP or a web server)
const char* server = "http://192.168.0.148:5003/data";

void setup() {
    Serial.begin(115200);
    dht.begin();

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi: ");
    Serial.println(ssid);
    
    // Wait for Wi-Fi connection
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println();
    Serial.println("Connected to Wi-Fi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());  // Print the ESP32's IP address
}

void loop() {
    // Read temperature and humidity
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Check if readings are valid
    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Failed to read from DHT sensor!");
        return;
    }

    // Send data to server
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;  // Create an HTTPClient object

        // Construct the URL properly
        String url = String(server) + "?temp=" + String(temperature) + "&humidity=" + String(humidity);
        
        http.begin(url);  // Start the HTTP request
        int httpCode = http.GET();  // Send the GET request

        // Check the response
        if (httpCode > 0) {
            String payload = http.getString();  // Get the response payload
            Serial.println("Server response: " + payload);
        } else {
            Serial.println("Error on HTTP request: " + String(httpCode));
        }

        http.end();  // Close the connection
    }

    delay(5000); // Wait 5 seconds before next reading
} 
