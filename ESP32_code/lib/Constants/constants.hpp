/*
UCSD ECE140B Team Driver Buddy
Constants for all sensors
Author: Abhijit Vadrevu

Reference: https://www.learncpp.com/cpp-tutorial/sharing-global-constants-across-multiple-files-using-inline-variables/
*/


#ifndef constants_hpp
#define constants_hpp

#include <ArduinoJson.h>


/*---------------------- USER MODIFYABLE CONSTANTS -----------*/
// Sensor Mode: Chooses which sensors to use
// Options: GPS_ID, IMU_ID, OBD_ID, ALL_ID
#define SENSOR_MODE ALL_ID


// Refresh Rate: How often to get data from sensors in HZ
// Reccomended: 1 - 4 Hz, 2 Hz is default
#define REFRESH_RATE_HZ 2


// CAN Bits: 11 bit or 29 bit CAN, depends on car
// Options: 1 for 11 bit, 0 for 29 bit
#define STANDARD_CAN_11BIT 1   


// CAN Pins: Tx Rx pins for OBD CAN module
#define CAN_TX_PIN  27           
#define CAN_RX_PIN  12  


// PIDS (Code to send to CAN module to get info from car) 
// See https://en.wikipedia.org/wiki/OBD-II_PIDs for more info
#define PID_ENGINE_RPM                           0x0C
#define PID_VEHICLE_SPEED                       0x0D
#define PID_THROTTLE_POSITION                   0x11


// Bluetooth UUIDs - Default UUIDs are for ESP32
#define SERVICE_UUID        "72458c8c-b270-4584-ae25-f6ea603648ac"
#define CHARACTERISTIC_UUID "ed106019-c201-4380-86fd-caf327906b87"

/*--------------------------------------------------------------*/



/*------------------ CONSTANTS (Do not Change) ------------------*/

// JSON Constants
#define DATA_SIZE 11
#define CAPACITY JSON_OBJECT_SIZE(DATA_SIZE)

// Sensor Constants
#define GPS_ID 0
#define IMU_ID 1
#define OBD_ID 2
#define ALL_ID 3

// CAN Constants
#if STANDARD_CAN_11BIT
#define CAN_ID_PID          0x7DF
#else
#define CAN_ID_PID          0x18db33f1
#endif

// IMU Constants
#define INTERRUPT_PIN 4  


#endif // constants_hpp