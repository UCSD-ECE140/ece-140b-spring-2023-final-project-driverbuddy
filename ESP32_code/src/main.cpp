#include "Arduino.h"
#include <sstream>
#include "gps.hpp"
#include "imu.hpp"
#include "obd_ii_driver.hpp"


GPS gps = GPS();
IMU imu = IMU();
OBD obd = OBD();

unsigned long REFRESH_RATE_HZ = 2;
unsigned long REFRESH_RATE_MS = 1000 / REFRESH_RATE_HZ;
unsigned long last_time = 0;

#define SENSOR_MODE 2   // 0 = GPS, 1 = IMU, 2 = OBD, 3 = ALL


void setup() {
  Serial.begin(115200);

  // Setup GPS
  gps.setup(17, 16);
  Serial.println("GPS setup complete");
  delay(2000);

  // Setup IMU
  bool imu_status = imu.setup(Serial);
  if (!imu_status) {
    Serial.println("IMU setup failed");
    while (1); // halt program if IMU setup fails
  }
  Serial.println("IMU setup complete");

  // Setup OBD
  bool obd_status = obd.setup(Serial);
  if (!obd_status) {
    Serial.println("OBD setup failed");
    while (1); // halt program if OBD setup fails
  }
  Serial.println("OBD setup complete");
}


void loop() {
	unsigned long current_time = millis();
	if (current_time - last_time > REFRESH_RATE_MS) {
		last_time = current_time;

		#if SENSOR_MODE == 0 || SENSOR_MODE == 3
			// Get GPS Data
			String latlon = "LatLon: " + gps.getLatLonString();
			Serial.println(latlon);
		#endif

		#if SENSOR_MODE == 1 || SENSOR_MODE == 3
			// Get IMU Data
			imu.update();
			Serial.println(imu.getQuaternionString() + " " + imu.getYawPitchRollString() + " " + imu.getAccelString());
		#endif

		#if SENSOR_MODE == 2 || SENSOR_MODE == 3
			// Get OBD Data
			OBDData obd_data = obd.get_OBD_data();
			std::stringstream obd_ss;
			obd_ss << "OBD: " << obd_data.engine_rpm << " " << obd_data.vehicle_speed << " " << obd_data.coolant_temp << std::endl;
			Serial.println(obd_ss.str().c_str());
		#endif
	}
}
