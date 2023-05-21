#include <Arduino.h>
#include <obd_ii_driver.hpp>

OBD::OBD() {}

OBD::~OBD() {}

bool OBD::setup(Stream &serial) {
    // Set up CAN
    can.begin(can_tx, can_rx, 9600);

    // Set CAN rate
    if (can.canRate(CAN_RATE_500)) {
        serial.println("CAN Init OK");
    }
    else {
        serial.println("CAN Init Failed");
        return false;
    }

    // Set Mask and Filter
    if (!set_mask_filt(serial)) {
        return false;
    }
    serial.println("OBD Init OK, starting...");
    return true;
}

OBDData OBD::get_OBD_data() {
    // Update OBD data by sending PIDs one at a time
    for (unsigned char pid : pid_list) {
        send_PID(pid);
        delay(50);
        receive_Can();
    }    
    return obd_data;
}


bool OBD::set_mask_filt(Stream &serial) {
    // Set Mask
    if (can.setMask(mask)) {
        serial.println("Set Mask OK");
    }
    else {
        serial.println("Set Mask Failed");
        return false;
    }

    // Set Filter
    if (can.setFilt(filt)) {
        serial.println("Set Filter OK");
    }
    else {
        serial.println("Set Filter Failed");
        return false;
    }
    return true;
}


void OBD::receive_Can() {
    // Receive CAN data
    unsigned long id = 0;
    unsigned char data[8];
    if (can.recv(&id, data)) {
        if(data[1] == 0x41) {
            // Check if PID is in dispatch table
            if (dispatch_table.find(data[2]) != dispatch_table.end()) {
                // Call function from dispatch table
                (this->*dispatch_table[data[2]])(data);
            }
        }
    }
}


void OBD::send_PID(unsigned char pid) {
    // Send PID with correct format for 11bit or 29bit CAN
    unsigned char tmp[8] = {0x02, 0x01, pid, 0, 0, 0, 0, 0};
    #if STANDARD_CAN_11BIT
        can.send(CAN_ID_PID, 0, 0, 8, tmp);   // SEND TO ID:0X55
    #else
        can.send(CAN_ID_PID, 1, 0, 8, tmp);   // SEND TO ID:0X55
    #endif
}


// Process PID functions
void OBD::process_engine_rpm(unsigned char *data) {
    obd_data.engine_rpm = (256.0*(float)data[3]+(float)data[4])/4.0;
}


void OBD::process_vehicle_speed(unsigned char *data) {
    obd_data.vehicle_speed = (float)data[3];
}


void OBD::process_coolant_temp(unsigned char *data) {
    obd_data.coolant_temp = (float)data[3]-40.0;
}