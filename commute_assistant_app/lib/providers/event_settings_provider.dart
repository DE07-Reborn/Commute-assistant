import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class EventSettingsProvider with ChangeNotifier {
  final ApiService apiService;

  bool _notifyBeforeDeparture = true;
  bool _notifyMask = true;
  bool _notifyUmbrella = true;
  bool _notifyClothing = true;
  bool _notifyMusic = true;
  bool _notifyBook = true;
  bool _isLoading = false;
  String? _error;

  EventSettingsProvider({required this.apiService});

  // Getters
  bool get notifyBeforeDeparture => _notifyBeforeDeparture;
  bool get notifyMask => _notifyMask;
  bool get notifyUmbrella => _notifyUmbrella;
  bool get notifyClothing => _notifyClothing;
  bool get notifyMusic => _notifyMusic;
  bool get notifyBook => _notifyBook;
  bool get isLoading => _isLoading;
  String? get error => _error;

  /// 알림 설정 로드
  Future<bool> loadEventSettings(int userId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await apiService.getEventSettings(userId);
      
      if (response != null) {
        _notifyBeforeDeparture = response['notify_before_departure'] ?? true;
        _notifyMask = response['notify_mask'] ?? true;
        _notifyUmbrella = response['notify_umbrella'] ?? true;
        _notifyClothing = response['notify_clothing'] ?? true;
        _notifyMusic = response['notify_music'] ?? true;
        _notifyBook = response['notify_book'] ?? true;
        _error = null;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = '알림 설정을 로드할 수 없습니다';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 알림 설정 업데이트 (출발 전 알림)
  Future<bool> setNotifyBeforeDeparture(int userId, bool value) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await apiService.updateEventSettings(userId, {
        'notify_before_departure': value,
      });

      if (response != null && response['success'] == true) {
        _notifyBeforeDeparture = value;
        _error = null;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = response?['message'] ?? '업데이트 실패';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 알림 설정 업데이트 (마스크)
  Future<bool> setNotifyMask(int userId, bool value) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await apiService.updateEventSettings(userId, {
        'notify_mask': value,
      });

      if (response != null && response['success'] == true) {
        _notifyMask = value;
        _error = null;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = response?['message'] ?? '업데이트 실패';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 알림 설정 업데이트 (우산)
  Future<bool> setNotifyUmbrella(int userId, bool value) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await apiService.updateEventSettings(userId, {
        'notify_umbrella': value,
      });

      if (response != null && response['success'] == true) {
        _notifyUmbrella = value;
        _error = null;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = response?['message'] ?? '업데이트 실패';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 알림 설정 업데이트 (옷 입기)
  Future<bool> setNotifyClothing(int userId, bool value) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await apiService.updateEventSettings(userId, {
        'notify_clothing': value,
      });

      if (response != null && response['success'] == true) {
        _notifyClothing = value;
        _error = null;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = response?['message'] ?? '업데이트 실패';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 알림 설정 업데이트 (음악)
  Future<bool> setNotifyMusic(int userId, bool value) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await apiService.updateEventSettings(userId, {
        'notify_music': value,
      });

      if (response != null && response['success'] == true) {
        _notifyMusic = value;
        _error = null;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = response?['message'] ?? '업데이트 실패';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// 알림 설정 업데이트 (도서)
  Future<bool> setNotifyBook(int userId, bool value) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await apiService.updateEventSettings(userId, {
        'notify_book': value,
      });

      if (response != null && response['success'] == true) {
        _notifyBook = value;
        _error = null;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = response?['message'] ?? '업데이트 실패';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
}
