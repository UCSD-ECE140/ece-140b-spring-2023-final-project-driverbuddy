#include "Arduino.h"
#include <sstream>
#include "gps.hpp"
#include "imu.hpp"
#include "obd_ii_driver.hpp"

#define GPS_ID 0
#define IMU_ID 1
#define OBD_ID 2
#define ALL_ID 3

// Set sensor mode and refresh rate here
#define SENSOR_MODE OBD_ID
unsigned long REFRESH_RATE_HZ = 2;

GPS gps = GPS();
IMU imu = IMU();
OBD obd = OBD(Serial);

unsigned long REFRESH_RATE_MS = 1000 / REFRESH_RATE_HZ;
unsigned long last_time = 0;


void setup() {
	Serial.begin(115200);

	#if SENSOR_MODE == GPS_ID || SENSOR_MODE == ALL_ID
		// Setup GPS
		gps.setup(17, 16);
		Serial.println("GPS setup complete");
		delay(2000);
	#endif

	#if SENSOR_MODE == IMU_ID || SENSOR_MODE == ALL_ID
		// Setup IMU
		bool imu_status = imu.setup(Serial);
		if (!imu_status) {
		Serial.println("IMU setup failed");
		while (1); // halt program if IMU setup fails
		}
		Serial.println("IMU setup complete");
	#endif

	#if SENSOR_MODE == OBD_ID || SENSOR_MODE == ALL_ID
		// Setup OBD
		obd.setup();
		Serial.println("OBD setup complete");
	#endif
}


void loop() {
	unsigned long current_time = millis();
	if (current_time - last_time > REFRESH_RATE_MS) {
		last_time = current_time;

		#if SENSOR_MODE == GPS_ID || SENSOR_MODE == ALL_ID
			// Get GPS Data
			String latlon = "LatLon: " + gps.getLatLonString();
			Serial.println(latlon);
		#endif

		#if SENSOR_MODE == IMU_ID || SENSOR_MODE == ALL_ID
			// Get IMU Data
			imu.update();
			Serial.println(imu.getQuaternionString() + " " + imu.getYawPitchRollString() + " " + imu.getAccelString());
		#endif

		#if SENSOR_MODE == OBD_ID || SENSOR_MODE == ALL_ID
			// Get OBD Data
			OBDData obd_data = obd.get_OBD_data();
			std::stringstream obd_ss;
			obd_ss << "OBD Data | " << "RPM: " << obd_data.engine_rpm; 
			obd_ss << "Speed: " << obd_data.vehicle_speed << "Coolant Temp: " << obd_data.coolant_temp;
			Serial.println(obd_ss.str().c_str());
		#endif
	}
}
