#ifndef obd_ii_driver_hpp
#define obd_ii_driver_hpp

#include <Arduino.h>
#include <obd_ii_rf.hpp>
#include <SoftwareSerial.h>
#include <Wire.h>

Serial_CAN can;

#define STANDARD_CAN_11BIT      1       // That depends on your car. some 1 some 0. 

#define can_tx  A0           // tx of serial can module connect to D2
#define can_rx  A1           // rx of serial can module connect to D3

#define PID_ENGIN_PRM       0x0C
#define PID_VEHICLE_SPEED   0x0D
#define PID_COOLANT_TEMP    0x05

#if STANDARD_CAN_11BIT
#define CAN_ID_PID          0x7DF
#else
#define CAN_ID_PID          0x18db33f1
#endif




#endif // obd_ii_driver_hpp