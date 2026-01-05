import 'recommendation_detail.dart';

class WeatherInfo {
  final double temperature;
  final String condition; // 'sunny', 'rainy', 'cloudy', 'snowy'
  final int humidity;
  final double windSpeed;
  final int description;
  final String? location;
  final String? weatherCategory; // 날씨 카테고리 (예: '맑음', '비', '눈', '흐림')

  WeatherInfo({
    required this.temperature,
    required this.condition,
    required this.humidity,
    required this.windSpeed,
    required this.description,
    this.location,
    this.weatherCategory,
  });
}

class Recommendation {
  final String clothing;
  final List<String> books;
  final List<String> music;
  final List<String>? bookLinks;  // 도서 링크 리스트
  final List<RecommendationDetail> clothingItems;

  Recommendation({
    required this.clothing,
    required this.books,
    required this.music,
    this.bookLinks,
    this.clothingItems = const [],
  });
}

