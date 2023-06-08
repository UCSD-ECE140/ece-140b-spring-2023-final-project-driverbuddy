////
////  ContentView.swift
////  DriverBuddyMain
////
////  Created by Joseph Katona on 6/2/23.
////
//
//
import SwiftUI
import MapKit
import CoreBluetooth
//import OAuth2
var service = BluetoothService()
var dataState : Bool = false
struct ContentView: View {
    var body: some View {
        NavigationStack(){
            VStack {
                WelcomeView()
            }.toolbar(.hidden, for: .navigationBar)
        }
    }
}
    struct DeviceView : View{
        var body: some View{
            VStack {
                Text("Bluetooth Status:")
                    .font(.title)
                if service.peripheralStatus == .connected{
                    Image(systemName: "wifi")
                        .resizable()
                        .frame(width: 100, height: 100)
                        .rotationEffect(.degrees(360))
                        .animation(Animation.linear.repeatForever(autoreverses: false))
                } else {
                    Image(systemName: "wifi.slash")
                        .resizable()
                        .frame(width: 100, height: 100)
                }
                Text(service.peripheralStatus.rawValue)
                    .font(.title)
                Text("\(service.magnetValue)")
                    .font(.largeTitle)
                    .fontWeight(.heavy)
                //
            }
            .padding()
        }
    }
    struct ContentView_Previews: PreviewProvider {
        static var previews: some View {
            ContentView()
        }
    }
    
    struct LoginView: View{
        @State private var username: String = ""
        @State private var password: String = ""
        @State var isloggedIn = false
        var body: some View{
            VStack{
                NavigationLink(destination: HomePageView(),
                                              isActive: $isloggedIn) { }
                Image("logo") // Replace "logo" with the name of your logo image
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
                
                Button(action: {
                    var theToken = requestToken(username : username,password : password)
                    debugPrint(theToken)
                    if theToken != "invalid"{
                        isloggedIn = true
                    }
                    
                }) {
                    Text("Login")
                        .foregroundColor(.white)
                        .padding()
                        .frame(width: 200)
                        .background(Color.blue)
                        .cornerRadius(10)
                }
                .padding(.top, 20)
                NavigationLink(destination: SignupView()) {
                    Text("Register Your account")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            }
        }
        
    }
    struct LoginView_Previews: PreviewProvider {
        static var previews: some View {
            LoginView()
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
                    
                    Stepper("Age: \(age)", value: $age, in: 15...100)
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
                    
                    Stepper("Car Year: \(carYear)", value: $carYear, in: 2000...2023)
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
    

struct HomePageView: View {
    @EnvironmentObject var sessionManager: SessionManager

    var body: some View {
        VStack {
            Text("Driver Buddy App")
                .font(.title)
                .padding()
            Spacer()
            NavigationLink(destination: StatsView()) {
                Text("Stats")
                    .font(.title2)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(10)
            }
            .padding()
            NavigationLink(destination: SearchView()) {
                Text("Drive")
                    .font(.title2)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.green)
                    .cornerRadius(10)
            }
            .padding()
            NavigationLink(destination: DeviceView()) {
                Text("Device Status")
                    .font(.title2)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.green)
                    .cornerRadius(10)
            }
            .padding()

            Button(action: {
                sessionManager.logout()
            }) {
                Text("Logout")
                    .font(.title2)
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.red)
                    .cornerRadius(10)
            }
            .padding()

            Spacer()
        }
    }
}
struct WelcomeView: View{
    var body: some View{
        VStack{
            TabView{
                firstpageView()
                secondPageView()
                thirdPageView()
            }
            .tabViewStyle(.page)
            .ignoresSafeArea()
        }
    }
}
struct firstpageView: View{
    var body: some View {
        VStack{
                Text("Welcome to Driver buddy!")
                    .cornerRadius(8)
                    .padding()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .font(.system(size: 50))
                Spacer()
                Divider()
            
        }
        .background(Color.blue)
    }
}

struct secondPageView: View{
    var body: some View {
        VStack{
            Text("Swipe right to login or register")
                .cornerRadius(8)
                .padding()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .font(.system(size: 50))
            Spacer()
            Divider()
            
        }
        .background(Color.blue)
    }
}
struct thirdPageView: View{
    var body: some View {
        VStack{
            NavigationLink(destination: LoginView()) {
                Text("Login")
                    .foregroundColor(.white)
                    .padding()
                    .frame(width: 200)
                    .background(Color.blue)
                    .cornerRadius(10)
            }
            NavigationLink(destination: SignupView()) {
                Text("Register Your account")
                    .foregroundColor(.white)
                    .padding()
                    .frame(width: 200)
                    .background(Color.blue)
                    .cornerRadius(10)
            }
        }.foregroundColor(.white)
            .padding()
            .frame(width: 200)
            .background(Color.blue)
            .cornerRadius(10)
    }
        
}
struct StatsView: View {
    var body: some View {
        Text("Stats View")
    }
}
struct DriveView: View {
    var body: some View {
        Text("Drive View")
    }
}

class SessionManager: ObservableObject {
    func logout() {
        // Perform logout logic
    }
}

struct WelcomeView_Previews: PreviewProvider {
    static var previews: some View {
        WelcomeView()
    }
}
