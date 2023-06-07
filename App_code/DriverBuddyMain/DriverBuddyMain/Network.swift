import SwiftUI
import Foundation
import Alamofire


let tokenUrl = "http://178.128.207.55/token"
let loginUrl = "http://178.128.207.55/login"

var token = "invalid"
func requestToken(username:String, password:String) -> String{
    let parameters = [
        "username": username,
        "password": password
    ]
    debugPrint(parameters)
    AF.request(tokenUrl,method: .post, parameters: parameters).validate().responseData { response in
//        var headers = response.response?.allHeaderFields
        //        let theCookie  = headers["Set-Cookie"]
        //        debugPrint(theCookie.value)
        let cookies = HTTPCookie.cookies(withResponseHeaderFields: response.response?.allHeaderFields as! [String: String], for: (response.response?.url!)!)
        token = cookies[0].value
        AF.session.configuration.httpCookieStorage?.setCookie(cookies[0])
        
        //        debugPrint(response.response?.allHeaderFields)
        
//        if token != "" {
////            debugPrint(token)
//            //        let headers: HTTPHeaders = [.authorization(bearerToken: token)]
//            var theRequest2 = AF.request(loginUrl,method: .post).validate().responseData{ response in
////                debugPrint(response)
//            }
//        }
    }
    return token
}
