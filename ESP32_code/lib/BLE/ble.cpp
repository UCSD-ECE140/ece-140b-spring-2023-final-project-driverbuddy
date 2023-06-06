#include <ble.hpp>


bool deviceConnected;


void BleServerCallbacks::onConnect(BLEServer* pServer) {
    deviceConnected = true;
    Serial.println("Device connected");
}


void BleServerCallbacks::onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
    Serial.println("Device disconnected");
}


BLE::BLE() {
    deviceConnected = false;
}


BLE::~BLE() {}


void BLE::setup() {
    Serial.println("BLE setup");
    
    // Create the BLE Device and Server
    BLEDevice::init("ESP32-DriverBuddy");
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new BleServerCallbacks());

    // Create Service and Characteristic
    BLEService *pService = pServer->createService(SERVICE_UUID);
    pCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ   |
        BLECharacteristic::PROPERTY_WRITE  |
        BLECharacteristic::PROPERTY_NOTIFY |
        BLECharacteristic::PROPERTY_INDICATE
    );
    pCharacteristic->addDescriptor(new BLE2902());

    // Start the service and begin Advertising
    pService->start();
    BLEAdvertising *pAdvertising = pServer->getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(false);
    pAdvertising->setMinPreferred(0x00); // set value to 0x00 to not advertise this parameter
    BLEDevice::startAdvertising();
    Serial.println("BLE setup done, waiting for device connection...");
}


bool BLE::is_connected() {
    return deviceConnected;
}


void BLE::send(String data) {
    if (deviceConnected) {
        Serial.println("Sending");
        pCharacteristic->setValue(data.c_str());
        pCharacteristic->notify();
    }
}
