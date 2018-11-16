#include "Particle.h"
// Port of TinyGPS for the Particle AssetTracker
// https://github.com/mikalhart/TinyGPSPlus
#include <TinyGPS++.h>
SYSTEM_THREAD(ENABLED)

void displayInfo();

// Set reporting intervals
unsigned long PUBLISH_PERIOD = 240000;
const unsigned long SERIAL_PERIOD = 30000;
 
// Set object aliases
TinyGPSPlus gps;
FuelGauge fuel;

// Set other variables
unsigned long lastSerial = 0;
unsigned long lastPublish = 0;
unsigned long startFix = 0;
bool gettingFix = false;
bool sent = false;

// Set geofence (use to filter out safe zones - e.g. 500m radius around the dragonhound's den.)
float lon_min = 115.933;
float lon_max = 115.936;
float lat_min = -32.032;
float lat_max = -32.028;
 
void setup()
{
    // Setup serial output
    Serial.begin(9600);
    
    // Connect to GPS module on Serial1 and D6
    Serial1.begin(9600);
    pinMode(D6, OUTPUT);
    digitalWrite(D6, LOW); // Settings D6 LOW powers up the GPS module
    
    startFix = millis();
    gettingFix = true;
Particle.connect();
}
 
void loop()
{
  while (Serial1.available() > 0) {
    if (gps.encode(Serial1.read())) {
      displayInfo();
    }
  }
}
 
void displayInfo() {
    
    // loops frequently for debugging
    if (millis() - lastSerial >= SERIAL_PERIOD) {
        lastSerial = millis();
     
        char buf[128];
        if (gps.location.isValid()) {
          snprintf(buf, sizeof(buf), "%f,%f,%.2f", gps.location.lat(), gps.location.lng(),fuel.getSoC());
            if (gettingFix) {
                gettingFix = false;
                unsigned long elapsed = millis() - startFix;
                Serial.printlnf("%lu milliseconds to get GPS fix", elapsed);
            }
        }
        else {
          strcpy(buf, "no location");
          if (!gettingFix) {
            gettingFix = true;
            startFix = millis();
          }
        }
        Serial.println(buf);
     
        // Publish GPS data to Particle.io
        if (millis() - lastPublish >= PUBLISH_PERIOD) {
            Serial.printlnf("Publishing");
            lastPublish = millis();
            sent = Particle.publish("G",buf, 60, PRIVATE);
        }
        
        // Send confirmation of publish to serial
        if (!sent) {
            Serial.printlnf("NOT sent");
        }
        else {
            Serial.printlnf("sent!");
        }        
        // Set GPS publish over 3G interval. If inside geofence, location is published less frequently to save on sim data usage
        if (gps.location.lng() > lon_max || gps.location.lng() < lon_min || gps.location.lat() > lat_max || gps.location.lat() < lat_min) {
            PUBLISH_PERIOD = 180000;
        }
        else {
            PUBLISH_PERIOD = 3600000;
        }
        // Publish interval slows down as battery charge reduces, to extend tracking time.
        PUBLISH_PERIOD = PUBLISH_PERIOD*60/fuel.getSoC();
    }    
}