// #include "Arduino.h"
// #include <sstream>
// #include "gps.hpp"
// #include "imu.hpp"
// #include "obd_ii_driver.hpp"

// #define GPS_ID 0
// #define IMU_ID 1
// #define OBD_ID 2
// #define ALL_ID 3

// // Set sensor mode and refresh rate here
// #define SENSOR_MODE OBD_ID
// unsigned long REFRESH_RATE_HZ = 2;

// GPS gps = GPS();
// IMU imu = IMU();
// OBD obd = OBD(Serial);

// unsigned long REFRESH_RATE_MS = 1000 / REFRESH_RATE_HZ;
// unsigned long last_time = 0;


// void setup() {
// 	Serial.begin(115200);

// 	#if SENSOR_MODE == GPS_ID || SENSOR_MODE == ALL_ID
// 		// Setup GPS
// 		gps.setup(17, 16);
// 		Serial.println("GPS setup complete");
// 		delay(2000);
// 	#endif

// 	#if SENSOR_MODE == IMU_ID || SENSOR_MODE == ALL_ID
// 		// Setup IMU
// 		bool imu_status = imu.setup(Serial);
// 		if (!imu_status) {
// 		Serial.println("IMU setup failed");
// 		while (1); // halt program if IMU setup fails
// 		}
// 		Serial.println("IMU setup complete");
// 	#endif

// 	#if SENSOR_MODE == OBD_ID || SENSOR_MODE == ALL_ID
// 		// Setup OBD
// 		obd.setup();
// 		Serial.println("OBD setup complete");
// 	#endif
// }


// void loop() {
// 	unsigned long current_time = millis();
// 	if (current_time - last_time > REFRESH_RATE_MS) {
// 		last_time = current_time;

// 		#if SENSOR_MODE == GPS_ID || SENSOR_MODE == ALL_ID
// 			// Get GPS Data
// 			String latlon = "LatLon: " + gps.getLatLonString();
// 			Serial.println(latlon);
// 		#endif

// 		#if SENSOR_MODE == IMU_ID || SENSOR_MODE == ALL_ID
// 			// Get IMU Data
// 			imu.update();
// 			Serial.println(imu.getQuaternionString() + " " + imu.getYawPitchRollString() + " " + imu.getAccelString());
// 		#endif

// 		#if SENSOR_MODE == OBD_ID || SENSOR_MODE == ALL_ID
// 			// Get OBD Data
// 			OBDData obd_data = obd.get_OBD_data();
// 			std::stringstream obd_ss;
// 			obd_ss << "OBD Data | " << "RPM: " << obd_data.engine_rpm; 
// 			obd_ss << "Speed: " << obd_data.vehicle_speed << "Coolant Temp: " << obd_data.coolant_temp;
// 			Serial.println(obd_ss.str().c_str());
// 		#endif
// 	}
// }


// Version 2

#include <obd_ii_rf.hpp>
#include <SoftwareSerial.h>

Serial_CAN can;

#define STANDARD_CAN_11BIT      0       // That depands on your car. some 1 some 0. 

#define can_tx  27           // tx of serial can module connect to D2
#define can_rx  12           // rx of serial can module connect to D3

#define PID_ENGIN_PRM       0x0C
#define PID_VEHICLE_SPEED   0x0D
#define PID_COOLANT_TEMP    0x05

#if STANDARD_CAN_11BIT
#define CAN_ID_PID          0x7DF
#else
#define CAN_ID_PID          0x18db33f1
#endif

unsigned char PID_INPUT;
unsigned char getPid    = 0;

#if STANDARD_CAN_11BIT
unsigned long mask[4] = 
{
    0, 0x7FC,                // ext, maks 0
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
    1, 0x1fffffff,               // ext, maks 0
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

void set_mask_filt()
{
    /*
     * set mask, set both the mask to 0x3ff
     */

    if(can.setMask(mask))
    {
        Serial.println("set mask ok");
    }
    else
    {
        Serial.println("set mask fail");
    }
    
    /*
     * set filter, we can receive id from 0x04 ~ 0x09
     */
    if(can.setFilt(filt))
    {
        Serial.println("set filt ok");
    }
    else 
    {
        Serial.println("set filt fail");
    }
    
}

void sendPid(unsigned char __pid)
{
    unsigned char tmp[8] = {0x02, 0x01, __pid, 0, 0, 0, 0, 0};
    Serial.print("SEND PID: 0x");
    Serial.println(__pid, HEX);

#if STANDARD_CAN_11BIT
    can.send(CAN_ID_PID, 0, 0, 8, tmp);   // SEND TO ID:0X55
#else
    can.send(CAN_ID_PID, 1, 0, 8, tmp);   // SEND TO ID:0X55
#endif

}

void setup()
{
    Serial.begin(115200);
    can.begin(can_tx, can_rx, 9600);      // tx, rx
    
    // set baudrate of CAN Bus to 500Kb/s
    if(can.canRate(CAN_RATE_500))
    {
        Serial.println("set can rate ok");
    }
    else
    {
        Serial.println("set can rate fail");
    }
    
    set_mask_filt();
    
    Serial.println("begin");
    
}


void taskCanRecv()
{
    unsigned char len = 0;
    unsigned long id  = 0;
    unsigned char buf[8];

    if(can.recv(&id, buf))                   // check if get data
    {
        Serial.println("\r\n------------------------------------------------------------------");
        Serial.print("Get Data From id: 0x");
        Serial.println(id, HEX);
        for(int i = 0; i<len; i++)          // print the data
        {
            Serial.print("0x");
            Serial.print(buf[i], HEX);
            Serial.print("\t");
        }
        Serial.println();
    }
}

void taskDbg()
{
    bool receiving = false;
    while(Serial.available())
    {
        receiving = true;
        char c = Serial.read();
        if(c>='0' && c<='9')
        {
            PID_INPUT *= 0x10;
            PID_INPUT += c-'0';
        }
        else if(c>='A' && c<='F')
        {
            PID_INPUT *= 0x10;
            PID_INPUT += 10+c-'A';
        }
        else if(c>='a' && c<='f')
        {
            PID_INPUT *= 0x10;
            PID_INPUT += 10+c-'a';
        }
    }
    if(receiving)
    {
        Serial.print("PID_INPUT: 0x");
        Serial.println(PID_INPUT, HEX);
        getPid = 1;
    }
}

void loop()
{
    taskCanRecv();
    taskDbg();
    
    if(getPid)          // GET A PID
    {
        getPid = 0;
        sendPid(PID_INPUT);
        PID_INPUT = 0;
    }
}