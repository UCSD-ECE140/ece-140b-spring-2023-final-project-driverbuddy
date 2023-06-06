#pragma once
#ifndef ble_hpp
#define ble_hpp

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <BLE2902.h>

#define SERVICE_UUID        "72458c8c-b270-4584-ae25-f6ea603648ac"
#define CHARACTERISTIC_UUID "ed106019-c201-4380-86fd-caf327906b87"


inline bool deviceConnected;


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