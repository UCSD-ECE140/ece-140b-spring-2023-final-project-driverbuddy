//
//  BLEScannerApp.swift
//  BLEScanner
//
//  Created by Christian Möller on 02.01.23.
//

import SwiftUI
import CoreBluetooth

//
//  ContentView.swift
//  BLEScanner
//
//  Created by Christian Möller on 02.01.23.
//



struct DiscoveredPeripheral {
    // Struct to represent a discovered peripheral
    var peripheral: CBPeripheral
    var advertisedData: String
}

class BluetoothScanner: NSObject, CBCentralManagerDelegate, ObservableObject {
    @Published var discoveredPeripherals = [DiscoveredPeripheral]()
    @Published var isScanning = false
    var centralManager: CBCentralManager!
    // Set to store unique peripherals that have been discovered
    var discoveredPeripheralSet = Set<CBPeripheral>()
    var timer: Timer?

    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: nil)
    }

    func startScan() {
        if centralManager.state == .poweredOn {
            // Set isScanning to true and clear the discovered peripherals list
            isScanning = true
            discoveredPeripherals.removeAll()
            discoveredPeripheralSet.removeAll()
            objectWillChange.send()

            // Start scanning for peripherals
            centralManager.scanForPeripherals(withServices: nil)

            // Start a timer to stop and restart the scan every 2 seconds
            timer?.invalidate()
            timer = Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { [weak self] timer in
                self?.centralManager.stopScan()
                self?.centralManager.scanForPeripherals(withServices: nil)
            }
        }
    }

    func stopScan() {
        // Set isScanning to false and stop the timer
        isScanning = false
        timer?.invalidate()
        centralManager.stopScan()
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .unknown:
            //print("central.state is .unknown")
            stopScan()
        case .resetting:
            //print("central.state is .resetting")
            stopScan()
        case .unsupported:
            //print("central.state is .unsupported")
            stopScan()
        case .unauthorized:
            //print("central.state is .unauthorized")
            stopScan()
        case .poweredOff:
            //print("central.state is .poweredOff")
            stopScan()
        case .poweredOn:
            //print("central.state is .poweredOn")
            startScan()
        @unknown default:
            print("central.state is unknown")
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        // Build a string representation of the advertised data and sort it by names
        var advertisedData = advertisementData.map { "\($0): \($1)" }.sorted(by: { $0 < $1 }).joined(separator: "\n")

        // Convert the timestamp into human readable format and insert it to the advertisedData String
        let timestampValue = advertisementData["kCBAdvDataTimestamp"] as! Double
        // print(timestampValue)
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "HH:mm:ss"
        let dateString = dateFormatter.string(from: Date(timeIntervalSince1970: timestampValue))

        advertisedData = "actual rssi: \(RSSI) dB\n" + "Timestamp: \(dateString)\n" + advertisedData

        // If the peripheral is not already in the list
        if !discoveredPeripheralSet.contains(peripheral) {
            // Add it to the list and the set
            discoveredPeripherals.append(DiscoveredPeripheral(peripheral: peripheral, advertisedData: advertisedData))
            discoveredPeripheralSet.insert(peripheral)
            objectWillChange.send()
        } else {
            // If the peripheral is already in the list, update its advertised data
            if let index = discoveredPeripherals.firstIndex(where: { $0.peripheral == peripheral }) {
                discoveredPeripherals[index].advertisedData = advertisedData
                objectWillChange.send()
            }
        }
    }
}
//
//  ContentView.swift
//  BLEScanner
//
//  Created by Christian Möller on 02.01.23.
//


struct ContentView: View {
    @ObservedObject private var bluetoothScanner = BluetoothScanner()
    @State private var searchText = ""

    var body: some View {
        VStack {
            HStack {
                // Text field for entering search text
                TextField("Search", text: $searchText)
                    .textFieldStyle(RoundedBorderTextFieldStyle())

                // Button for clearing search text
                Button(action: {
                    self.searchText = ""
                }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
                .buttonStyle(PlainButtonStyle())
                .opacity(searchText == "" ? 0 : 1)
            }
            .padding()

            // List of discovered peripherals filtered by search text
            List(bluetoothScanner.discoveredPeripherals.filter {
                self.searchText.isEmpty ? true : $0.peripheral.name?.lowercased().contains(self.searchText.lowercased()) == true
            }, id: \.peripheral.identifier) { discoveredPeripheral in
                VStack(alignment: .leading) {
                    Text(discoveredPeripheral.peripheral.name ?? "Unknown Device")
                    Text(discoveredPeripheral.advertisedData)
                        .font(.caption)
                        .foregroundColor(.gray)
                }
            }

            // Button for starting or stopping scanning
            Button(action: {
                if self.bluetoothScanner.isScanning {
                    self.bluetoothScanner.stopScan()
                } else {
                    self.bluetoothScanner.startScan()
                }
            }) {
                if bluetoothScanner.isScanning {
                    Text("Stop Scanning")
                } else {
                    Text("Scan for Devices")
                }
            }
            // Button looks cooler this way on iOS
            .padding()
            .background(bluetoothScanner.isScanning ? Color.red : Color.blue)
            .foregroundColor(Color.white)
            .cornerRadius(5.0)
        }
    }
}
struct BLEScannerApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
