import SwiftUI
import Foundation
import Alamofire


let tokenUrl = "http://178.128.207.55/token"
let loginUrl = "http://178.128.207.55/login"
let registerUrl = "http://178.128.207.55/register"
let dataUrl = "http://178.128.207.55/post_driving_data"
let calcscoreUrl = "http://178.128.207.55/calculate_score"
var token = "invalid"
func requestToken(username:String, password:String) -> String{
    let parameters = [
        "username": username,
        "password": password
    ]
    AF.request(tokenUrl,method: .post, parameters: parameters).validate().responseData { response in
        var headers = response.response?.allHeaderFields
        if headers != nil{
            let cookies = HTTPCookie.cookies(withResponseHeaderFields:  headers as! [String: String], for: (response.response?.url!)!)
            debugPrint(cookies)
            if !cookies.isEmpty{
                token = cookies[0].value
                AF.session.configuration.httpCookieStorage?.setCookie(cookies[0])
            }
        }
       
        
    }
    return token
}

func registerUser(username: String, email : String, first_name : String, last_name : String, car_make : String, car_model : String, car_year: Int, password : String){
    
    let parameters = [
        "username": username,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "car_make": car_make,
        "car_model": car_model,
        "car_year": car_year,
        "password": password,
        "confirm_password": password
    ] as [String : Any]
    AF.request(tokenUrl,method: .post, parameters: parameters).validate().responseData { response in
        debugPrint(response.data!)
    }
}

func postData(ax : Double, ay : Double, az : Double, pitch : Double, yaw : Double, roll : Double, latitude : Double, longitude : Double){
    let parameters = [
      "accel_x": ax,
      "accel_y": ay,
      "accel_z": az,
      "yaw": yaw,
      "pitch": pitch,
      "roll": roll,
      "throttle_position": 0,
      "vehicle_speed": 0,
      "engine_rpm": 0,
      "latitude": latitude,
      "longitude": longitude,
      "timestamp": 0
    ]
    AF.request(dataUrl,method: .post, parameters: parameters, encoding: JSONEncoding.default).validate().responseData { response in
        debugPrint(response.data!)
    }
}

func calcScore(){
    AF.request(calcscoreUrl,method: .get).validate().responseData { response in
        debugPrint(response.data!)
    }
}
