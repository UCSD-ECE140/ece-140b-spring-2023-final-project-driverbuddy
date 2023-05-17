#include "Arduino.h"
#include "gps.hpp"
#include "imu.hpp"


GPS gps = GPS();
IMU imu = IMU();

void setup() {
  Serial.begin(115200);
  gps.setup(17, 16);
  Serial.println("GPS setup complete");
  delay(2000);
  bool imu_status = imu.setup(Serial);
  if (!imu_status) {
    Serial.println("IMU setup failed");
    while (1); // halt program if IMU setup fails
  }
  Serial.println("IMU setup complete");
}


void loop() {
  // Get GPS Data
  String latlon = "LatLon: " + gps.getLatLonString();
  Serial.println(latlon);

  // Get IMU Data
  imu.update();
  Serial.println(imu.getQuaternionString() + " " + imu.getYawPitchRollString() + " " + imu.getAccelString());
  delay(500);
}
