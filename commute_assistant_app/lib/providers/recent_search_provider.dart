import 'package:flutter/foundation.dart';
import '../models/recent_search.dart';

class RecentSearchProvider with ChangeNotifier {
  List<RecentSearch> _searches = [
    RecentSearch(
      id: '1',
      origin: '강남역',
      destination: '홍대입구역',
      searchTime: DateTime.now().subtract(const Duration(hours: 1)),
    ),
  ];

  List<RecentSearch> get searches => _searches;

  void addSearch(String origin, String destination) {
    final search = RecentSearch(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      origin: origin,
      destination: destination,
      searchTime: DateTime.now(),
    );
    _searches.insert(0, search);
    // 최대 10개만 유지
    if (_searches.length > 10) {
      _searches = _searches.take(10).toList();
    }
    notifyListeners();
  }

  void clearSearches() {
    _searches.clear();
    notifyListeners();
  }
}

