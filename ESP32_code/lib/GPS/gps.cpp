#include <gps.hpp>


GPS::GPS(){}

GPS::~GPS()
{
    Serial1.end();
}

void GPS::setup(int tx_pin, int rx_pin)
{
    Serial1.begin(9600, SERIAL_8N1, rx_pin, tx_pin);
    delay(1000);
}

double GPS::getLatitude()
{
    waitForLocation();
    if (!gps.location.isValid())
    {
        return 0.0;
    }
    return gps.location.lat();
}

double GPS::getLongitude()
{
    waitForLocation();
    if (!gps.location.isValid())
    {
        return 0.0;
    }
    return gps.location.lng();
}

String GPS::getLatLonString()
{
    waitForLocation();
    if (!gps.location.isValid())
    {
        return "INVALID";
    }
    return String(gps.location.lat(), 6) + "," + String(gps.location.lng(), 6);
}

void GPS::waitForLocation()
{
    while (Serial1.available() > 0)
    {
        if (gps.encode(Serial1.read())) {
            break;
        }
    }
}