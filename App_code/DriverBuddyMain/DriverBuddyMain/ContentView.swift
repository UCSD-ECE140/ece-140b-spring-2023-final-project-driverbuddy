////
////  ContentView.swift
////  DriverBuddyMain
////
////  Created by Joseph Katona-Work on 6/2/23.
////
//
//
import SwiftUI
import MapKit

struct ContentView: View {
    @State private var username: String = ""
    @State private var password: String = ""
    @StateObject var service = BluetoothService()
    var body: some View {
        NavigationView(){
            VStack {
                Text(service.peripheralStatus.rawValue)
                                .font(.title)
                            Text("\(service.magnetValue)")
                                .font(.largeTitle)
                                .fontWeight(.heavy)
//                Image("logo") // Replace "logo" with the name of your logo image
//
//                TextField("Username", text: $username)
//                    .padding()
//                    .background(Color.gray.opacity(0.2))
//                    .cornerRadius(10)
//                    .padding(.horizontal, 50)
//
//                SecureField("Password", text: $password)
//                    .padding()
//                    .background(Color.gray.opacity(0.2))
//                    .cornerRadius(10)
//                    .padding(.horizontal, 50)
//
//                Button(action: {
//                    // Perform login action here
//                    // You can add your authentication logic
//                }) {
//                    Text("Login")
//                        .foregroundColor(.white)
//                        .padding()
//                        .frame(width: 200)
//                        .background(Color.blue)
//                        .cornerRadius(10)
//                }
//                .padding(.top, 20)
//                NavigationLink(destination: SignupView()) {
//                    Text("Register Your account")
//                        .padding()
//                        .background(Color.blue)
//                        .foregroundColor(.white)
//                        .cornerRadius(10)
//                }
            }
            .padding()
        }
        
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}


struct SignupView: View {
    @State private var username: String = ""
    @State private var password: String = ""
    @State private var age: Int = 0
    @State private var carModel: String = ""
    @State private var carMake: String = ""
    @State private var carYear: Int = 0
    @State private var email: String = ""
    @State private var firstName: String = ""
    @State private var lastName: String = ""
    
    var body: some View {
        
        VStack {
            Image("logo") // Replace "logo" with the name of your logo image
            Group {
                TextField("First Name", text: $firstName)
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(10)
                    .padding(.horizontal, 50)
                
                TextField("Last Name", text: $lastName)
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(10)
                    .padding(.horizontal, 50)
                TextField("Username", text: $username)
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(10)
                    .padding(.horizontal, 50)
                
                SecureField("Password", text: $password)
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(10)
                    .padding(.horizontal, 50)
                
                Stepper("Age: \(age)", value: $age, in: 18...100)
                    .padding(.horizontal, 50)
                
                TextField("Car Model", text: $carModel)
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(10)
                    .padding(.horizontal, 50)
                
                TextField("Car Make", text: $carMake)
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(10)
                    .padding(.horizontal, 50)
                
                Stepper("Car Year: \(carYear)", value: $carYear, in: 1900...2023)
                    .padding(.horizontal, 50)
                
                TextField("Email", text: $email)
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .cornerRadius(10)
                    .padding(.horizontal, 50)
                    .keyboardType(.emailAddress)
            }
            
            Button(action: {
                // Perform signup action here
                // You can add your registration logic
            }) {
                Text("Sign Up")
                    .foregroundColor(.white)
                    .padding()
                    .frame(width: 200)
                    .background(Color.blue)
                    .cornerRadius(10)
            }
            .padding(.top, 20)
        }
        .padding()
    }
}


struct SignupView_Previews: PreviewProvider {
    static var previews: some View {
        SignupView()
    }
}
struct MapView: View {
    // 2.
    @State private var region = MKCoordinateRegion(
                center: CLLocationCoordinate2D(
                    latitude: 40.83834587046632,
                    longitude: 14.254053016537693),
                span: MKCoordinateSpan(
                    latitudeDelta: 0.03,
                    longitudeDelta: 0.03)
                )

    var body: some View {
        // 3.
        Map(coordinateRegion: $region)
            .edgesIgnoringSafeArea(.all)
//        Image(systemName: "speedometer")
//                      .resizable()
//                      .aspectRatio(contentMode: .fit)
//                      .frame(width: 50, height: 50)
//
//                  Text("(speedLimit)")
//                      .font(.headline)
              }
    }

struct MapView_Previews: PreviewProvider {
    static var previews: some View {
        MapView()
    }
}

struct DriverScoreView: View {
    let score: Int
    
    var body: some View {
        VStack(spacing: 8) {
            Text("Driver Score")
                .font(.title)
            
            Text("\(score)")
                .font(.system(size: 80, weight: .bold, design: .rounded))
                .foregroundColor(scoreColor)
        }
    }
    
    var scoreColor: Color {
        if score >= 80 {
            return .green
        } else if score >= 60 {
            return .yellow
        } else {
            return .red
        }
    }
}

struct DriverScore_Previews: PreviewProvider {
    static var previews: some View {
        DriverScoreView(score: 80)
    }
}

