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
