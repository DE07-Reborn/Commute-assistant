import Flutter
import UIKit
import GoogleMaps

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // Google Maps API 키 설정 - YOUR_API_KEY를 실제 키로 교체하세요
    GMSServices.provideAPIKey("AIzaSyD0R-e5sVfzsjbpq1g_hY4eS452dZ4ZL78")
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
