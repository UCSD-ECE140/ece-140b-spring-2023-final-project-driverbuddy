/*
UCSD ECE140B Team Driver Buddy
OBD-II RF Dev Kit Driver
Author: Abhijit Vadrevu

- OBD-II RF Dev Kit Library by Longan Labs: https://github.com/Longan-Labs/OBD_II_RF_Dev_Kit_Library
- Link to specific example referenced: https://github.com/Longan-Labs/OBD_II_RF_Dev_Kit_Library/blob/96bd230d070a962b247b0136567c7a88dfa667fd/examples/obd_demo2/obd_demo2.ino
*/


#ifndef obd_ii_driver_hpp
#define obd_ii_driver_hpp

#include <Arduino.h>
#include <ArduinoJson.h>
#include <obd_ii_rf.hpp>
#include <map>
#include <vector>
#include <string>
#include <constants.hpp>


struct OBDData {
    float engine_rpm;
    float vehicle_speed;
    float throttle_position;
};


class OBD {
public:
    OBD();
    ~OBD();
    void setup();
    void get_OBD_data(StaticJsonDocument<JSON_OBJECT_SIZE(11)>& data);

private:
    // Variables
    Serial_CAN can;
    OBDData obd_data;
    unsigned long start_time = 0;

    // Functions
    bool set_mask_filt();
    bool receive_Can();
    void send_PID(unsigned char pid);
    std::string get_OBD_data_string(unsigned char *data, int len);

    void process_engine_rpm(unsigned char *data);
    void process_vehicle_speed(unsigned char *data);
    void process_throttle_position(unsigned char *data);


    // Map Dispatch Table
    std::map<unsigned char, void (OBD::*)(unsigned char *)> process_dispatch {
        {PID_ENGINE_RPM, &OBD::process_engine_rpm},
        {PID_VEHICLE_SPEED, &OBD::process_vehicle_speed},
        {PID_THROTTLE_POSITION, &OBD::process_throttle_position}
    };

    // PID List
    std::vector<unsigned char> pid_list = {PID_ENGINE_RPM, PID_VEHICLE_SPEED, PID_THROTTLE_POSITION};
};


#endif // obd_ii_driver_hpp