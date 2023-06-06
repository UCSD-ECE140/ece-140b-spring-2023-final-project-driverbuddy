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


OBD::OBD() {}


OBD::~OBD() {}


void OBD::setup() {
    // Set up CAN
    can.begin(CAN_TX_PIN, CAN_RX_PIN, 9600);
    Serial.println(can.canRate(CAN_RATE_500) ? "CAN Init OK" : "CAN Init Fail");
    Serial.println(set_mask_filt() ? "Set Mask OK" : "Set Mask Fail");
    Serial.println("OBD Init OK, starting...");
}


void OBD::get_OBD_data(StaticJsonDocument<JSON_OBJECT_SIZE(11)>& data) {
    // Update OBD data by sending PIDs one at a time
    for (auto& pid : pid_list) {
        Serial.print("Sending PID: ");
        Serial.println(pid, HEX);
        send_PID(pid);
        start_time = millis();

        // Wait for response w/ timeout
        while (!receive_Can()) {
            if (millis() - start_time > 500) {
                Serial.println("Timeout");
                break;
            }
        }
    }
    data["engine_rpm"] = obd_data.engine_rpm;
    data["vehicle_speed"] = obd_data.vehicle_speed;
    data["throttle_position"] = obd_data.throttle_position;
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
        Serial.println(get_OBD_data_string(data, 8).c_str());
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
    Serial.println("Raw RPM: ");
    Serial.print(data[3], HEX);
    Serial.print(data[4], HEX);
}


void OBD::process_vehicle_speed(unsigned char *data) {
    obd_data.vehicle_speed = (float)data[3];
    Serial.println("Raw Speed: ");
    Serial.print(data[3], HEX);
}


void OBD::process_throttle_position(unsigned char *data) {
    obd_data.throttle_position = (float)data[3]*100.0/255.0;
    Serial.println("Raw Coolant Temp: ");
    Serial.print(data[3], HEX);
}