/*
UCSD ECE140B Team Driver Buddy
MPU6050 IMU Driver
Author: Abhijit Vadrevu

- MPU6050 Library by Electronic Cats: https://github.com/ElectronicCats/mpu6050
- Link to specific example referenced: https://github.com/ElectronicCats/mpu6050/blob/master/examples/MPU6050_DMP6/MPU6050_DMP6.ino
*/

#ifndef imu_hpp
#define imu_hpp

#include <Arduino.h>
#include <ArduinoJson.h>
#include <I2Cdev.h>
#include <MPU6050_6Axis_MotionApps20.h>
#include <Wire.h>
#include <constants.hpp>



extern volatile bool mpuInterrupt;     // indicates whether MPU interrupt pin has gone high
void dmpDataReady();


class IMU
{
public:
    IMU();
    ~IMU();
    bool setup(Stream &serial);
    void update();
    String get_quat_string();
    String get_ypr_string();
    String get_accel_string();
    void update_and_get_data(StaticJsonDocument<CAPACITY>& data);

private:

    // MPU Object
    MPU6050 mpu;

    // Data
    Quaternion quaternion;
    float euler[3];
    VectorInt16 accel;
    VectorInt16 accelReal;
    VectorInt16 accelWorld;
    VectorFloat gravity;

    // MPU control/status vars
    bool dmpReady = false;  // set true if DMP init was successful
    uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
    uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
    uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
    uint16_t fifoCount;     // count of all bytes currently in FIFO
    uint8_t fifoBuffer[64]; // FIFO storage buffer

};





#endif // imu_hpp
