//
//  BluetoothService.swift
//  DriverBuddyMain
//
//  Created by Joseph Katona-Work on 6/4/23.
//

import Foundation
import CoreBluetooth

enum ConnectionStatus : String{
    case connected
    case disconnected
    case scanning
    case connecting
    case error
}

let DriverBuddyService: CBUUID = CBUUID(string: "72458c8c-b270-4584-ae25-f6ea603648ac")
let DriverBuddyCharecteristic: CBUUID = CBUUID(string: "ed106019-c201-4380-86fd-caf327906b87")

class BluetoothService: NSObject, ObservableObject{
    private var centralManager: CBCentralManager!
    
    var DriverPeripheral: CBPeripheral?
    @Published var peripheralStatus: ConnectionStatus = .disconnected
    @Published var magnetValue: Int = 0
    override init(){
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: nil)
    }
    func scanForPeripherals(){
        peripheralStatus = .scanning
        centralManager.scanForPeripherals(withServices: nil)
    }
}

extension BluetoothService: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if central.state == .poweredOn{
            print("CB Powered On")
            scanForPeripherals()
        }
    }
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        debugPrint(peripheral)
        if peripheral.name == "ESP32-DriverBuddy"{
            print("Discovered \(peripheral.name ?? "no name")")
            DriverPeripheral = peripheral
            centralManager.connect(peripheral)
            peripheralStatus = .connecting
        }
    }
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        peripheralStatus = .connected
        peripheral.delegate = self
        peripheral.discoverServices([DriverBuddyService])
        centralManager.stopScan()
    }
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        peripheralStatus = .disconnected
    }
    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        peripheralStatus = .error
        print(error?.localizedDescription ?? "no error")
    }
}

extension BluetoothService: CBPeripheralDelegate{
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        for service in peripheral.services ?? [] {
            debugPrint(service)
            if service.uuid == DriverBuddyService{
                
                peripheral.discoverCharacteristics([DriverBuddyCharecteristic], for: service)
            }
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        for characteristic in service.characteristics ?? [] {
//            debugPrint(characteristic)
            peripheral.setNotifyValue(true, for: characteristic)
            print("found characteristic, waiting on values.")
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
//        debugPrint(characteristic.uuid)
        if characteristic.uuid == DriverBuddyCharecteristic{
            guard let data = characteristic.value else{
                print("No data received for \(characteristic.uuid.uuidString)")
                return
            }
            let sensorData: String = String(decoding: data, as: UTF8.self)
//            debugPrint(sensorData)
            let dict = convertToDictionary(text: sensorData)
            if dataState == true{
                postData(ax: dict?["accel_x"] as! Double, ay: dict?["accel_y"] as! Double, az: dict?["accel_z"] as! Double, pitch: dict?["pitch"] as! Double, yaw: dict?["yaw"] as! Double, roll: dict?["roll"] as! Double, latitude: dict?["lat"] as! Double, longitude: dict?["lon"] as! Double)
            }
        }
    }
}

func convertToDictionary(text: String) -> [String: Any]? {
    if let data = text.data(using: .utf8) {
        do {
            return try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any]
        } catch {
            print(error.localizedDescription)
        }
    }
    return nil
}
