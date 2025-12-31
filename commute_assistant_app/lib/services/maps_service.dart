import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/route_info.dart';

class MapsService {
  static const String _baseUrl = 'https://maps.googleapis.com/maps/api';
  final String apiKey;

  MapsService({required this.apiKey});

  Future<List<RouteInfo>> getRoutes({
    required String origin,
    required String destination,
  }) async {
    final routes = <RouteInfo>[];
    
    try {
      print('Searching route from: $origin to: $destination');
      
      // Geocoding으로 좌표 변환
      print('Geocoding origin: $origin');
      final originCoords = await _geocodeAddress(origin);
      if (originCoords == null) {
        print('Failed to geocode origin address');
        return routes;
      }
      print('Origin coordinates: ${originCoords['lat']}, ${originCoords['lng']}');
      
      print('Geocoding destination: $destination');
      final destCoords = await _geocodeAddress(destination);
      if (destCoords == null) {
        print('Failed to geocode destination address');
        return routes;
      }
      print('Destination coordinates: ${destCoords['lat']}, ${destCoords['lng']}');

      // 모든 이동 수단으로 경로 검색
      final travelModes = ['transit', 'driving', 'walking', 'bicycling'];
      
      // 좌표를 문자열로 변환 (더 정확한 요청)
      final originStr = '${originCoords['lat']},${originCoords['lng']}';
      final destStr = '${destCoords['lat']},${destCoords['lng']}';
      
      for (final mode in travelModes) {
        try {
          print('Searching route with mode: $mode');
          
          // 좌표 기반 요청
          // Google Maps Directions API는 모든 이동 수단을 지원합니다
          // avoid 파라미터를 제거하고, units=metric 추가
          // 일부 지역에서는 avoid 파라미터가 문제를 일으킬 수 있음
          String directionsUrlStr = '$_baseUrl/directions/json?origin=$originStr&destination=$destStr&mode=$mode&key=$apiKey&language=ko&region=kr&units=metric';
          
          // 대중교통의 경우 여러 경로 옵션을 받기 위해 alternatives=true 추가
          if (mode == 'transit') {
            directionsUrlStr += '&alternatives=true';
          } else {
            directionsUrlStr += '&alternatives=false';
          }
          
          final directionsUrl = Uri.parse(directionsUrlStr);
          
          print('$mode mode URL: ${directionsUrl.toString().replaceAll(apiKey, 'API_KEY_HIDDEN')}');

          final response = await http.get(directionsUrl);
          print('$mode mode HTTP Status: ${response.statusCode}');
          
          if (response.statusCode == 200) {
            final data = json.decode(response.body);
            print('$mode mode Response Status: ${data['status']}');
            
            // ZERO_RESULTS인 경우 응답 전체를 로깅
            if (data['status'] == 'ZERO_RESULTS') {
              print('$mode mode Full Response: ${response.body}');
            }
            
            if (data['status'] == 'OK' && data['routes'] != null && (data['routes'] as List).isNotEmpty) {
              // 대중교통의 경우 여러 경로 옵션을 모두 가져오기
              final routesList = data['routes'] as List;
              
              // 대중교통의 경우 실제로 다른 경로만 필터링
              List<dynamic> uniqueRoutes = [];
              if (mode == 'transit') {
                // 경로를 비교하여 중복 제거
                for (var routeOption in routesList) {
                  bool isDuplicate = false;
                  final routeLeg = routeOption['legs'][0];
                  final routeDistance = routeLeg['distance']['text'];
                  final routeDuration = routeLeg['duration']['text'];
                  
                  // 기존 경로들과 비교
                  for (var existingRoute in uniqueRoutes) {
                    final existingLeg = existingRoute['legs'][0];
                    final existingDistance = existingLeg['distance']['text'];
                    final existingDuration = existingLeg['duration']['text'];
                    
                    // 거리와 소요 시간이 같으면 중복으로 간주
                    if (routeDistance == existingDistance && routeDuration == existingDuration) {
                      // 추가로 대중교통 구성도 비교
                      final routeSteps = routeLeg['steps'] as List?;
                      final existingSteps = existingLeg['steps'] as List?;
                      
                      if (routeSteps != null && existingSteps != null) {
                        // TRANSIT step의 개수와 타입 비교
                        final routeTransitTypes = <String>[];
                        final existingTransitTypes = <String>[];
                        
                        for (var step in routeSteps) {
                          if (step['travel_mode'] == 'TRANSIT') {
                            final transit = step['transit_details'];
                            final vehicleType = transit?['line']?['vehicle']?['type'] ?? '';
                            final name = transit?['line']?['short_name'] ?? transit?['line']?['name'] ?? '';
                            routeTransitTypes.add('$vehicleType:$name');
                          }
                        }
                        
                        for (var step in existingSteps) {
                          if (step['travel_mode'] == 'TRANSIT') {
                            final transit = step['transit_details'];
                            final vehicleType = transit?['line']?['vehicle']?['type'] ?? '';
                            final name = transit?['line']?['short_name'] ?? transit?['line']?['name'] ?? '';
                            existingTransitTypes.add('$vehicleType:$name');
                          }
                        }
                        
                        // 대중교통 구성이 같으면 중복
                        if (routeTransitTypes.length == existingTransitTypes.length) {
                          bool sameComposition = true;
                          for (int i = 0; i < routeTransitTypes.length; i++) {
                            if (routeTransitTypes[i] != existingTransitTypes[i]) {
                              sameComposition = false;
                              break;
                            }
                          }
                          if (sameComposition) {
                            isDuplicate = true;
                            break;
                          }
                        }
                      } else {
                        // step이 없으면 거리/시간만으로 판단
                        isDuplicate = true;
                        break;
                      }
                    }
                  }
                  
                  if (!isDuplicate) {
                    uniqueRoutes.add(routeOption);
                    if (uniqueRoutes.length >= 3) break; // 최대 3개까지만
                  }
                }
                
                print('$mode mode: Found ${routesList.length} route(s), ${uniqueRoutes.length} unique route(s)');
              } else {
                uniqueRoutes = [routesList[0]]; // 다른 이동 수단은 첫 번째만
              }
              
              for (int routeIndex = 0; routeIndex < uniqueRoutes.length; routeIndex++) {
                final route = uniqueRoutes[routeIndex];
                final leg = route['legs'][0];
                
                final distance = leg['distance']['text'];
                final duration = leg['duration']['text'];
                
                print('$mode mode route ${routeIndex + 1} - Distance: $distance, Duration: $duration');
                
                // 대중교통 정보 추출 (상세 정보 포함)
                final transitOptions = <TransitInfo>[];
                if (mode == 'transit' && route['legs'] != null && (route['legs'] as List).isNotEmpty) {
                  final steps = leg['steps'] as List?;
                  if (steps != null) {
                    print('Total steps in transit route ${routeIndex + 1}: ${steps.length}');
                    for (var step in steps) {
                      final travelMode = step['travel_mode'];
                      print('Step travel_mode: $travelMode');
                      
                      if (travelMode == 'TRANSIT') {
                        final transit = step['transit_details'];
                        if (transit == null) {
                          print('Warning: transit_details is null');
                          continue;
                        }
                        
                        final vehicle = transit['line']?['vehicle'];
                        final type = vehicle?['type'] ?? 'UNKNOWN';
                        final name = transit['line']?['short_name'] ?? transit['line']?['name'] ?? '알 수 없음';
                        
                        print('Transit type: $type, name: $name');
                        
                        // 시간 정보
                        final departureTime = transit['departure_time']?['text'] ?? '';
                        final arrivalTime = transit['arrival_time']?['text'] ?? '';
                        final arrivalValue = transit['arrival_time']?['value'] ?? 0;
                        final arrivalMinutes = _calculateMinutesUntilArrival(arrivalValue);
                        
                        // 역/정류장 정보
                        final departureStop = transit['departure_stop'];
                        final arrivalStop = transit['arrival_stop'];
                        final stationName = departureStop?['name'] ?? '';
                        final departureStationName = arrivalStop?['name'] ?? '';
                        
                        // 구간 정보
                        final stepDuration = step['duration']?['text'] ?? '';
                        final numStops = transit['num_stops'] ?? 0;

                        // 버스와 지하철 모두 처리
                        final transitType = (type == 'BUS' || type == 'BUSES') ? 'bus' : 'subway';
                        
                        print('Adding transit: $transitType - $name from $stationName to $departureStationName');

                        transitOptions.add(TransitInfo(
                          type: transitType,
                          name: name,
                          arrivalTime: arrivalTime,
                          arrivalMinutes: arrivalMinutes,
                          stationName: stationName,
                          departureStationName: departureStationName,
                          duration: stepDuration,
                          numStops: numStops,
                          departureTime: departureTime,
                        ));
                      } else if (travelMode == 'WALKING') {
                        // 도보 구간도 표시 (환승을 위한 도보)
                        final walkingDuration = step['duration']?['text'] ?? '';
                        final walkingDistance = step['distance']?['text'] ?? '';
                        if (walkingDuration.isNotEmpty && transitOptions.isNotEmpty) {
                          print('Walking segment: $walkingDistance, $walkingDuration');
                        }
                      }
                    }
                    print('Total transit options extracted for route ${routeIndex + 1}: ${transitOptions.length}');
                    for (var opt in transitOptions) {
                      print('  - ${opt.type}: ${opt.name}');
                    }
                  }
                }

                // 실제 경로 폴리라인 추출
                final routePoints = <RoutePoint>[];
                final overviewPolyline = route['overview_polyline'];
                if (overviewPolyline != null && overviewPolyline['points'] != null) {
                  final points = _decodePolyline(overviewPolyline['points']);
                  routePoints.addAll(points);
                }

                final routeInfo = RouteInfo(
                  origin: origin,
                  destination: destination,
                  originLat: originCoords['lat'] as double,
                  originLng: originCoords['lng'] as double,
                  destLat: destCoords['lat'] as double,
                  destLng: destCoords['lng'] as double,
                  distance: distance,
                  duration: duration,
                  transitOptions: transitOptions,
                  routePoints: routePoints,
                  travelMode: mode,
                );
                
                routes.add(routeInfo);
                print('$mode mode route ${routeIndex + 1} added successfully. Total routes: ${routes.length}');
              }
            } else if (data['status'] == 'ZERO_RESULTS') {
              // ZERO_RESULTS인 경우, 주소 기반으로 재시도
              print('$mode mode ZERO_RESULTS with coordinates, trying with address...');
              
              if (mode != 'transit') { // transit은 이미 성공했으므로 제외
                try {
                  final addressUrl = Uri.parse(
                    '$_baseUrl/directions/json?origin=${Uri.encodeComponent(origin)}&destination=${Uri.encodeComponent(destination)}&mode=$mode&key=$apiKey&language=ko&region=kr&units=metric',
                  );
                  
                  final addressResponse = await http.get(addressUrl);
                  if (addressResponse.statusCode == 200) {
                    final addressData = json.decode(addressResponse.body);
                    print('$mode mode address fallback Response Status: ${addressData['status']}');
                    
                    if (addressData['status'] == 'OK' && addressData['routes'] != null && (addressData['routes'] as List).isNotEmpty) {
                      final route = addressData['routes'][0];
                      final leg = route['legs'][0];
                      
                      final distance = leg['distance']['text'];
                      final duration = leg['duration']['text'];
                      
                      final routePoints = <RoutePoint>[];
                      final overviewPolyline = route['overview_polyline'];
                      if (overviewPolyline != null && overviewPolyline['points'] != null) {
                        final points = _decodePolyline(overviewPolyline['points']);
                        routePoints.addAll(points);
                      }

                      routes.add(RouteInfo(
                        origin: origin,
                        destination: destination,
                        originLat: originCoords['lat'] as double,
                        originLng: originCoords['lng'] as double,
                        destLat: destCoords['lat'] as double,
                        destLng: destCoords['lng'] as double,
                        distance: distance,
                        duration: duration,
                        transitOptions: [],
                        routePoints: routePoints,
                        travelMode: mode,
                      ));
                      print('$mode mode route added with address fallback. Total routes: ${routes.length}');
                    } else {
                      print('$mode mode address fallback also failed: ${addressData['status']}');
                    }
                  }
                } catch (e) {
                  print('$mode mode address fallback error: $e');
                }
              }
            } else {
              print('$mode mode failed: ${data['status']} - ${data['error_message'] ?? 'No error message'}');
            }
          } else {
            print('$mode mode HTTP error: ${response.statusCode} - ${response.body}');
          }
        } catch (e, stackTrace) {
          print('Error getting route for $mode: $e');
          print('Stack trace: $stackTrace');
          // 다음 이동 수단으로 계속
        }
      }
      
      print('Total routes found: ${routes.length}');
      for (var route in routes) {
        print('  - ${route.travelMode}: ${route.distance}, ${route.duration}');
      }
      
      // 이동 수단별로 정렬: 대중교통, 자가용, 자전거, 걷기 순서
      final modeOrder = {'transit': 0, 'driving': 1, 'bicycling': 2, 'walking': 3};
      routes.sort((a, b) {
        final orderA = modeOrder[a.travelMode] ?? 99;
        final orderB = modeOrder[b.travelMode] ?? 99;
        return orderA.compareTo(orderB);
      });
      
      return routes;
    } catch (e) {
      print('Error getting routes: $e');
      return routes;
    }
  }

  Future<Map<String, double>?> _geocodeAddress(String address) async {
    try {
      final url = Uri.parse(
        '$_baseUrl/geocode/json?address=${Uri.encodeComponent(address)}&key=$apiKey&language=ko',
      );
      final response = await http.get(url);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'OK' && data['results'].isNotEmpty) {
          final location = data['results'][0]['geometry']['location'];
          return {
            'lat': location['lat'].toDouble(),
            'lng': location['lng'].toDouble(),
          };
        }
      }
      return null;
    } catch (e) {
      print('Error geocoding: $e');
      return null;
    }
  }

  int _calculateMinutesUntilArrival(int arrivalTimestamp) {
    final now = DateTime.now().millisecondsSinceEpoch ~/ 1000;
    final minutes = (arrivalTimestamp - now) ~/ 60;
    return minutes > 0 ? minutes : 0;
  }

  /// Google Maps의 인코딩된 폴리라인을 디코딩하여 좌표 리스트로 변환
  List<RoutePoint> _decodePolyline(String encoded) {
    final List<RoutePoint> points = [];
    int index = 0;
    int lat = 0;
    int lng = 0;

    while (index < encoded.length) {
      int shift = 0;
      int result = 0;
      int byte;

      do {
        byte = encoded.codeUnitAt(index++) - 63;
        result |= (byte & 0x1F) << shift;
        shift += 5;
      } while (byte >= 0x20);

      int deltaLat = ((result & 1) != 0) ? ~(result >> 1) : (result >> 1);
      lat += deltaLat;

      shift = 0;
      result = 0;

      do {
        byte = encoded.codeUnitAt(index++) - 63;
        result |= (byte & 0x1F) << shift;
        shift += 5;
      } while (byte >= 0x20);

      int deltaLng = ((result & 1) != 0) ? ~(result >> 1) : (result >> 1);
      lng += deltaLng;

      points.add(RoutePoint(
        lat: lat / 1e5,
        lng: lng / 1e5,
      ));
    }

    return points;
  }
}

