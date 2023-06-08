//
//  SwiftUIView.swift
//  DriverBuddyMain
//
//  Created by Andy Fong on 6/2/23.
//

import SwiftUI
import Alamofire

//let statsURL = "http://178.128.207.55/get_driving_stats"
//
//AF.request(tokenUrl, method: .get, parameters: parameters).validate().responseData { response in

struct StatsView: View {
    
    // Averages of columns
    @State private var avgDriverScore: Double = 0.75
    @State private var avgRouteScore: Double = 0.5
    @State private var avgStabilityScore: Double = 0.25
    // Sums of columns
    @State private var hardBrakes: Int16 = 10
    @State private var hardAccels: Int16 = 20
    @State private var harshCornerings: Int16 = 30
    @State private var totalMiles: Double = 40.27
    
    var body: some View {
        ScrollView{
            VStack(spacing: 10) {
                Text("Average Scores")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white)
                    .padding(.bottom, 5)
                    .padding(.top, 5)
                
                VStack(spacing: 10) {
                    Group {
                        HStack(spacing: 50) {
                            VStack{
                                Text("Driver Score")
                                    .foregroundColor(.white)
                                CircleView(title: "\(avgDriverScore*100)", trimValue: avgDriverScore, color: "red")
                            }
                        }
                        HStack(spacing: 50) {
                            VStack {
                                Text("Route Score")
                                    .foregroundColor(.white)
                                CircleView(title: "\(avgRouteScore*100)", trimValue: avgRouteScore, color: "green")
                            }
                            VStack {
                                Text("Stability Score")
                                    .foregroundColor(.white)
                                CircleView(title: "\(avgStabilityScore*100)", trimValue: avgStabilityScore, color: "blue")
                            }
                        }
                    }
                }
                
                Text("Lifetime Stats")
                    .foregroundColor(.white)
                    .font(.system(size: 20, weight: .bold))
                    .padding(.top, 10)
                
                VStack(spacing: 10) {
                    Group {
                        CategoryView(name: "Hard Braking Instances", value: "\(hardBrakes)")
                        CategoryView(name: "Hard Acceleration Instances", value: "\(hardAccels)")
                        CategoryView(name: "Sharp/Wide Turns", value: "\(harshCornerings)")
                        CategoryView(name: "Total Miles Driven", value: "\(totalMiles) miles")
                    }
                }
                
                Text("Past Trips")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.white)
                    .padding(.top, 20)
                
                TableView()
                
                Spacer()
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color.black)
    }
}

func CircleView(title: String, trimValue: Double, color: String) -> some View {
    
    if color == "red"{
        return ZStack {
            Circle()
                .trim(from: 0, to: CGFloat(trimValue))
                .stroke(Color.red, lineWidth: 4)
                .frame(width: 80, height: 80)

            Text(title)
                .foregroundColor(.white)
        }
    }
    else if color == "green"{
        return ZStack {
            Circle()
                .trim(from: 0, to: CGFloat(trimValue))
                .stroke(Color.green, lineWidth: 4)
                .frame(width: 80, height: 80)

            Text(title)
                .foregroundColor(.white)
        }
    }
    else if color == "blue"{
        return ZStack {
            Circle()
                .trim(from: 0, to: CGFloat(trimValue))
                .stroke(Color.blue, lineWidth: 4)
                .frame(width: 80, height: 80)

            Text(title)
                .foregroundColor(.white)
        }
    }
    return ZStack {
        Circle()
            .trim(from: 0, to: CGFloat(trimValue))
            .stroke(Color.black, lineWidth: 4)
            .frame(width: 80, height: 80)

        Text(title)
            .foregroundColor(.white)
    }
}

struct CategoryView: View {
    var name: String
    var value: String
    
    var body: some View {
        HStack {
            Text(name)
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(.white)
            Spacer()
            Text(value)
                .foregroundColor(.white)
                .font(.system(size: 12))
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 10)
        .background(Color.gray.opacity(0.2))
        .cornerRadius(10)
    }
}

struct TableView: View {
    var body: some View {
        VStack(spacing: 10) {
            HStack {
                Group {
                    Text("Date")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white)
                    Spacer()
                    Text("Miles")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white)
                    Spacer()
                    Text("Driver Score")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white)
                    Spacer()
                    Text("Eco Score")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white)
                    Spacer()
                }
                Group {
                    Text("Stability Score")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white)
                    Spacer()
                    Text("Hard Brakes")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white)
                    Spacer()
                    Text("Hard Accelerations")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white)
                    Spacer()
                    Text("Sharp/Wide Turns")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(.white)
                }
            }
            
            // Example rows, replace with your data
            TableRow(rowData: ("6/1", "20.4", "87", "84", "69", "2", "1", "0"))
            TableRow(rowData: ("6/2", "15.3", "73", "78", "69", "5", "1", "2"))
            TableRow(rowData: ("6/3", "4.8", "90", "88", "83", "0", "2", "1"))
        }
        .padding(.horizontal, 20)
        .background(Color.gray.opacity(0.2))
        .cornerRadius(10)
    }
}

struct TableRow: View {
    var rowData: (String, String, String, String, String, String, String, String)
    
    var body: some View {
        HStack {
            Group {
                Text(rowData.0)
                    .font(.system(size: 11))
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .foregroundColor(.white)
                Spacer()
                Text(rowData.1)
                    .font(.system(size: 11))
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .foregroundColor(.white)
                Spacer()
                Text(rowData.2)
                    .font(.system(size: 11))
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .foregroundColor(.white)
                Spacer()
                Text(rowData.3)
                    .font(.system(size: 11))
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .foregroundColor(.white)
                Spacer()
            }
            Group {
                
                Text(rowData.4)
                    .font(.system(size: 11))
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .foregroundColor(.white)
                Spacer()
                Text(rowData.5)
                    .font(.system(size: 11))
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .foregroundColor(.white)
                Spacer()
                Text(rowData.6)
                    .font(.system(size: 11))
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .foregroundColor(.white)
                Spacer()
                Text(rowData.7)
                    .font(.system(size: 11))
                    .frame(maxWidth: .infinity, alignment: .trailing)
                    .foregroundColor(.white)
            }
        }
    }
}

struct StatsView_Previews: PreviewProvider {
    static var previews: some View {
        StatsView()
    }
}
