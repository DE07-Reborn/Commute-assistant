class RouteInfo {
  final String origin;
  final String destination;
  final double originLat;
  final double originLng;
  final double destLat;
  final double destLng;
  final String distance;
  final String duration;
  final List<TransitInfo> transitOptions;
  final List<RoutePoint> routePoints; // 실제 경로 좌표 리스트
  final String travelMode; // 'driving', 'walking', 'bicycling', 'transit'

  RouteInfo({
    required this.origin,
    required this.destination,
    required this.originLat,
    required this.originLng,
    required this.destLat,
    required this.destLng,
    required this.distance,
    required this.duration,
    required this.transitOptions,
    required this.routePoints,
    required this.travelMode,
  });
}

class RoutePoint {
  final double lat;
  final double lng;

  RoutePoint({required this.lat, required this.lng});
}

class TransitInfo {
  final String type; // 'bus' or 'subway'
  final String name;
  final String arrivalTime;
  final int arrivalMinutes;
  final String stationName; // 승차역/정류장
  final String departureStationName; // 하차역/정류장
  final String duration; // 해당 구간 소요 시간
  final int numStops; // 정거장 수
  final String departureTime; // 출발 시간

  TransitInfo({
    required this.type,
    required this.name,
    required this.arrivalTime,
    required this.arrivalMinutes,
    required this.stationName,
    this.departureStationName = '',
    this.duration = '',
    this.numStops = 0,
    this.departureTime = '',
  });
}

