#include <Arduino.h>
#include <ArduinoJson.h>
#include <sstream>
#include <gps.hpp>
#include <imu.hpp>
#include <obd_ii_driver.hpp>
#include <ble.hpp>


#define GPS_ID 0
#define IMU_ID 1
#define OBD_ID 2
#define ALL_ID 3

// Set sensor mode and refresh rate here
#define SENSOR_MODE ALL_ID
unsigned long REFRESH_RATE_HZ = 2;

GPS gps = GPS();
IMU imu = IMU();
OBD obd = OBD(Serial);
BLE ble = BLE();


unsigned long REFRESH_RATE_MS = 1000 / REFRESH_RATE_HZ;
unsigned long last_time = 0;
const int capacity = JSON_OBJECT_SIZE(11);


void setup() {
	Serial.begin(115200);
    ble.setup();

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
        StaticJsonDocument<capacity> data;
        std::stringstream data_ss;        

		#if SENSOR_MODE == GPS_ID || SENSOR_MODE == ALL_ID
			// Get GPS Data
            gps.getLatLon(data);
            data_ss << "GPS Data | " << "Lat: " << data["lat"] << " Lon: " << data["lon"] << "\n";
		#endif

		#if SENSOR_MODE == IMU_ID || SENSOR_MODE == ALL_ID
			// Get IMU Data
            imu.update_and_get_data(data);
            data_ss << "IMU Data | " << "Pitch: " << data["pitch"] << " Roll: " << data["roll"] << " Yaw: " << data["yaw"];
            data_ss << " Accel X: " << data["accel_x"] << " Accel Y: " << data["accel_y"] << " Accel Z: " << data["accel_z"] << "\n";
		#endif

		#if SENSOR_MODE == OBD_ID || SENSOR_MODE == ALL_ID
			// Get OBD Data
            obd.get_OBD_data(data);
            data_ss << "OBD Data | " << "Speed: " << data["speed"] << " RPM: " << data["rpm"] << " Throttle: " << data["throttle"] << "\n";
		#endif

        // Send data over BLE
        String data_str;
        serializeJson(data, data_str);
        ble.send(data_str);
	}
}
