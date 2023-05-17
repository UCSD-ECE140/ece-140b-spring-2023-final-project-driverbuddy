#ifndef gps_hpp
#define gps_hpp

#include <Arduino.h>
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

private:
    TinyGPSPlus gps;
    void waitForLocation();
};

#endif // gps_hpp
