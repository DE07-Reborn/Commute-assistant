import 'package:flutter/foundation.dart';
import '../models/route_info.dart';
import '../services/maps_service.dart';

class RouteProvider with ChangeNotifier {
  final MapsService _mapsService;
  RouteInfo? _routeInfo;
  List<RouteInfo> _routes = []; // 여러 경로 옵션
  bool _isLoading = false;
  String? _error;

  RouteProvider({required MapsService mapsService})
      : _mapsService = mapsService;

  RouteInfo? get routeInfo => _routeInfo;
  List<RouteInfo> get routes => _routes;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> searchRoute({
    required String origin,
    required String destination,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final routes = await _mapsService.getRoutes(
        origin: origin,
        destination: destination,
      );

      if (routes.isNotEmpty) {
        _routes = routes;
        _routeInfo = routes[0]; // 첫 번째 경로를 기본으로 선택
        _error = null;
      } else {
        _error = '경로를 찾을 수 없습니다.';
        _routeInfo = null;
        _routes = [];
      }
    } catch (e) {
      _error = '경로 검색 중 오류가 발생했습니다: $e';
      _routeInfo = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void selectRoute(RouteInfo route) {
    _routeInfo = route;
    notifyListeners();
  }

  void clearRoute() {
    _routeInfo = null;
    _routes = [];
    _error = null;
    notifyListeners();
  }
}

