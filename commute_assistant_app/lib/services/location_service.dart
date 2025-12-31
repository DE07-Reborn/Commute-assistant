import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';

/// 현재 위치를 가져오는 서비스
class LocationService {
  /// 위치 권한 요청 및 현재 위치 가져오기
  Future<Position?> getCurrentPosition() async {
    try {
      // 위치 서비스 활성화 확인
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        print('위치 서비스가 비활성화되어 있습니다.');
        return null;
      }

      // 위치 권한 확인
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          print('위치 권한이 거부되었습니다.');
          return null;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        print('위치 권한이 영구적으로 거부되었습니다.');
        return null;
      }

      // 현재 위치 가져오기
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      return position;
    } catch (e) {
      print('현재 위치 가져오기 오류: $e');
      return null;
    }
  }

  /// 좌표를 주소로 변환
  Future<String?> getAddressFromCoordinates(double latitude, double longitude) async {
    try {
      List<Placemark> placemarks = await placemarkFromCoordinates(latitude, longitude);
      if (placemarks.isNotEmpty) {
        Placemark place = placemarks[0];
        // 한국 주소 형식으로 변환
        String address = '';
        if (place.country != null) address += place.country!;
        if (place.administrativeArea != null) address += ' ${place.administrativeArea}';
        if (place.locality != null) address += ' ${place.locality}';
        if (place.street != null) address += ' ${place.street}';
        return address.trim();
      }
      return null;
    } catch (e) {
      print('좌표를 주소로 변환 오류: $e');
      return null;
    }
  }

  /// 두 좌표 간의 거리 계산 (미터 단위)
  double calculateDistance(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    return Geolocator.distanceBetween(lat1, lon1, lat2, lon2);
  }

  /// 두 위치가 같은지 확인 (기준: 1km 이내)
  bool isSameLocation(
    double? lat1,
    double? lon1,
    double? lat2,
    double? lon2, {
    double thresholdMeters = 1000.0,
  }) {
    if (lat1 == null || lon1 == null || lat2 == null || lon2 == null) {
      return false;
    }
    final distance = calculateDistance(lat1, lon1, lat2, lon2);
    return distance <= thresholdMeters;
  }
}

