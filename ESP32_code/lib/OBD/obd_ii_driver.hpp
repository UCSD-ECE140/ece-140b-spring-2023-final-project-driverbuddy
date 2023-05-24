#ifndef obd_ii_driver_hpp
#define obd_ii_driver_hpp

#include <Arduino.h>
#include <obd_ii_rf.hpp>
#include <map>
#include <vector>
#include <string>

#define STANDARD_CAN_11BIT      1       // That depends on your car. some 1 some 0. 

// CAN module pins
#define can_tx  27           
#define can_rx  12      

// PIDS (Code to send to CAN module to get info from car)
#define PID_ENGIN_PRM       0x0C
#define PID_VEHICLE_SPEED   0x0D
#define PID_THROTTLE_POSITION 0x11
#define PID_RELATIVE_ACCELERATOR_PEDAL_POSITION 0x5a



#if STANDARD_CAN_11BIT
#define CAN_ID_PID          0x7DF
#else
#define CAN_ID_PID          0x18db33f1
#endif


struct OBDData {
    float engine_rpm;
    float vehicle_speed;
    float coolant_temp;
};


class OBD {
public:
    OBD(Stream &serial);
    ~OBD();
    void setup();
    OBDData get_OBD_data();

private:
    // Variables
    Serial_CAN can;
    OBDData obd_data;
    Stream &serial;
    unsigned long start_time = 0;

    // Functions
    bool set_mask_filt();
    bool receive_Can();
    void send_PID(unsigned char pid);
    std::string get_OBD_data_string(unsigned char *data, int len);

    void process_engine_rpm(unsigned char *data);
    void process_vehicle_speed(unsigned char *data);
    void process_coolant_temp(unsigned char *data);

    // Map Dispatch Table
    std::map<unsigned char, void (OBD::*)(unsigned char *)> process_dispatch {
        {PID_ENGIN_PRM, &OBD::process_engine_rpm},
        {PID_VEHICLE_SPEED, &OBD::process_vehicle_speed},
        {PID_COOLANT_TEMP, &OBD::process_coolant_temp}
    };

    // PID List
    std::vector<unsigned char> pid_list = {PID_ENGIN_PRM, PID_VEHICLE_SPEED, PID_COOLANT_TEMP};
};


#endif // obd_ii_driver_hpp