#ifndef obd_ii_driver_hpp
#define obd_ii_driver_hpp

#include <Arduino.h>
#include <obd_ii_rf.hpp>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <map>

#define STANDARD_CAN_11BIT      1       // That depends on your car. some 1 some 0. 

// CAN module pins
#define can_tx  19           
#define can_rx  18      

// PIDS (Code to send to CAN module to get info from car)
#define PID_ENGIN_PRM       0x0C
#define PID_VEHICLE_SPEED   0x0D
#define PID_COOLANT_TEMP    0x05

#if STANDARD_CAN_11BIT
#define CAN_ID_PID          0x7DF
#else
#define CAN_ID_PID          0x18db33f1
#endif

#if STANDARD_CAN_11BIT
unsigned long mask[4] = 
{
    0, 0x7FC,                // ext, mask 0
    0, 0x7FC,                // ext, mask 1
};

unsigned long filt[12] = 
{
    0, 0x7E8,                // ext, filt 0
    0, 0x7E8,                // ext, filt 1
    0, 0x7E8,                // ext, filt 2
    0, 0x7E8,                // ext, filt 3
    0, 0x7E8,                // ext, filt 4
    0, 0x7E8,                // ext, filt 5
};

#else
unsigned long mask[4] =
{
    1, 0x1fffffff,               // ext, mask 0
    1, 0x1fffffff,
};
 
unsigned long filt[12] =
{
    1, 0x18DAF110,                // ext, filt
    1, 0x18DAF110,                // ext, filt 1
    1, 0x18DAF110,                // ext, filt 2
    1, 0x18DAF110,                // ext, filt 3
    1, 0x18DAF110,                // ext, filt 4
    1, 0x18DAF110,                // ext, filt 5
};
#endif

struct OBDData {
    float engine_rpm;
    float vehicle_speed;
    float coolant_temp;
};


class OBD {
public:
    OBD();
    ~OBD();
    bool setup(Stream &serial);
    OBDData get_OBD_data();

private:
    // Variables
    Serial_CAN can;
    OBDData obd_data;

    // Functions
    bool set_mask_filt(Stream &serial);
    void receive_Can();
    void send_PID(unsigned char pid);

    void process_engine_rpm(unsigned char *data);
    void process_vehicle_speed(unsigned char *data);
    void process_coolant_temp(unsigned char *data);

    // Map Dispatch Table
    std::map<unsigned char, void (OBD::*)(unsigned char *)> dispatch_table {
        {PID_ENGIN_PRM, &OBD::process_engine_rpm},
        {PID_VEHICLE_SPEED, &OBD::process_vehicle_speed},
        {PID_COOLANT_TEMP, &OBD::process_coolant_temp}
    };

    // PID List
    unsigned char pid_list[3] = {PID_ENGIN_PRM, PID_VEHICLE_SPEED, PID_COOLANT_TEMP};

};


#endif // obd_ii_driver_hpp