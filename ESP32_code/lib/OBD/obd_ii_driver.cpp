#include <obd_ii_driver.hpp>

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
    1, 0x18DAF110,                // ext, filt 0
    1, 0x18DAF110,                // ext, filt 1
    1, 0x18DAF110,                // ext, filt 2
    1, 0x18DAF110,                // ext, filt 3
    1, 0x18DAF110,                // ext, filt 4
    1, 0x18DAF110,                // ext, filt 5
};
#endif


OBD::OBD(Stream &serial) : serial(serial) {}

OBD::~OBD() {}

void OBD::setup() {
    // Set up CAN
    can.begin(can_tx, can_rx, 9600);
    serial.println(can.canRate(CAN_RATE_500) ? "CAN Init OK" : "CAN Init Fail");
    serial.println(set_mask_filt() ? "Set Mask OK" : "Set Mask Fail");
    serial.println("OBD Init OK, starting...");
}

OBDData OBD::get_OBD_data() {
    // Update OBD data by sending PIDs one at a time
    for (auto& pid : pid_list) {
        serial.print("Sending PID: ");
        serial.println(pid, HEX);
        send_PID(pid);
        start_time = millis();

        // Wait for response w/ timeout
        while (!receive_Can()) {
            if (millis() - start_time > 1000) {
                serial.println("Timeout");
                break;
            }
        }
    }    
    return obd_data;
}


bool OBD::set_mask_filt() {
    if (!can.setMask(mask)) {
        return false;
    }
    if (!can.setFilt(filt)) {
        return false;    
    }
    return true;
}


bool OBD::receive_Can() {
    // Receive CAN data
    unsigned long id = 0;
    unsigned char data[8];
    if (can.recv(&id, data)) {
        serial.println(get_OBD_data_string(data, 8).c_str());
        if(data[1] == 0x41) {
            // Check if PID is in dispatch table
            if (process_dispatch.find(data[2]) != process_dispatch.end()) {
                // Call function from dispatch table
                (this->*process_dispatch[data[2]])(data);
                return true;
            }
        }
    }
    return false;
}

std::string OBD::get_OBD_data_string(unsigned char *data, int len) {
    std::string str_data = "";
    for (int i = 0; i < len; i++) {
        str_data += data[i];
    }
    return str_data;
}

void OBD::send_PID(unsigned char pid) {
    // Send PID with correct format for 11bit or 29bit CAN
    unsigned char packet[8] = {0x02, 0x01, pid, 0, 0, 0, 0, 0};
    #if STANDARD_CAN_11BIT
    can.send(CAN_ID_PID, 0, 0, 8, packet);   // SEND TO ID:0X55
    #else
    can.send(CAN_ID_PID, 1, 0, 8, packet);   // SEND TO ID:0X55
    #endif
}


// Process PID functions
void OBD::process_engine_rpm(unsigned char *data) {
    obd_data.engine_rpm = (256.0*(float)data[3]+(float)data[4])/4.0;
    serial.println("Raw RPM: ");
    serial.print(data[3], HEX);
    serial.print(data[4], HEX);
}


void OBD::process_vehicle_speed(unsigned char *data) {
    obd_data.vehicle_speed = (float)data[3];
    serial.println("Raw Speed: ");
    serial.print(data[3], HEX);
}


void OBD::process_coolant_temp(unsigned char *data) {
    obd_data.coolant_temp = (float)data[3]-40.0;
    serial.println("Raw Coolant Temp: ");
    serial.print(data[3], HEX);
}