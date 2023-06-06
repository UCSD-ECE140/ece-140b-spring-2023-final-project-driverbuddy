/*
UCSD ECE140B Team Driver Buddy
MPU6050 IMU Driver
Author: Abhijit Vadrevu

- TinyGPSPlus Library by Mikal Hart: https://github.com/Tinyu-Zhao/TinyGPSPlus-ESP32
- Link to specific example referenced: https://registry.platformio.org/libraries/mikalhart/TinyGPSPlus/examples/DeviceExample/DeviceExample.ino
*/


#ifndef gps_hpp
#define gps_hpp

#include <Arduino.h>
#include <ArduinoJson.h>
#include <TinyGPSPlus.h>


class GPS
{
public:
    GPS();
    ~GPS();
    void setup(int tx_pin, int rx_pin);
    double getLatitude();
    double getLongitude();
    String getLatLonString();
    void getLatLon(StaticJsonDocument<JSON_OBJECT_SIZE(11)>& data);

private:
    TinyGPSPlus gps;
    void waitForLocation();
};





#endif // gps_hpp
