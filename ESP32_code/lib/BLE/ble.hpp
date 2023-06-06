/*
UCSD ECE140B Team Driver Buddy
Bluetooth Low Energy (BLE) Server
Author: Abhijit Vadrevu

- Reference: https://www.youtube.com/watch?v=5K8W1j_dC3U
*/


#ifndef ble_hpp
#define ble_hpp

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <BLE2902.h>
#include <constants.hpp>


class BleServerCallbacks: public BLEServerCallbacks {
public:
    void onConnect(BLEServer* pServer);
    void onDisconnect(BLEServer* pServer);
};


class BLE {
public:
    BLE();
    ~BLE();
    void setup();
    void send(String data);
    bool is_connected();

private:
    BLEServer *pServer;
    BLECharacteristic *pCharacteristic;
};


#endif /* ble_hpp */