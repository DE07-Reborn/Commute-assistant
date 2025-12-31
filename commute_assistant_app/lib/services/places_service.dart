import 'dart:convert';
import 'package:http/http.dart' as http;

class PlacePrediction {
  final String placeId;
  final String description;
  final String mainText;
  final String secondaryText;

  PlacePrediction({
    required this.placeId,
    required this.description,
    required this.mainText,
    required this.secondaryText,
  });

  factory PlacePrediction.fromJson(Map<String, dynamic> json) {
    final structuredFormatting = json['structured_formatting'] ?? {};
    return PlacePrediction(
      placeId: json['place_id'] ?? '',
      description: json['description'] ?? '',
      mainText: structuredFormatting['main_text'] ?? '',
      secondaryText: structuredFormatting['secondary_text'] ?? '',
    );
  }
}

class PlacesService {
  static const String _baseUrl = 'https://maps.googleapis.com/maps/api';
  final String apiKey;

  PlacesService({required this.apiKey});

  /// 대한민국 주소 자동완성 검색
  Future<List<PlacePrediction>> getPlacePredictions(String input) async {
    if (input.isEmpty) {
      return [];
    }

    try {
      final url = Uri.parse(
        '$_baseUrl/place/autocomplete/json?input=${Uri.encodeComponent(input)}&key=$apiKey&language=ko&components=country:kr',
      );

      final response = await http.get(url);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'OK' || data['status'] == 'ZERO_RESULTS') {
          final predictions = data['predictions'] as List?;
          if (predictions != null) {
            return predictions
                .map((p) => PlacePrediction.fromJson(p as Map<String, dynamic>))
                .toList();
          }
        }
      }
      return [];
    } catch (e) {
      print('Error getting place predictions: $e');
      return [];
    }
  }

  /// Place ID로 상세 정보 가져오기 (주소, 좌표 등)
  Future<Map<String, dynamic>?> getPlaceDetails(String placeId) async {
    try {
      final url = Uri.parse(
        '$_baseUrl/place/details/json?place_id=$placeId&key=$apiKey&language=ko&fields=formatted_address,geometry,name',
      );

      final response = await http.get(url);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (data['status'] == 'OK') {
          final result = data['result'];
          final location = result['geometry']['location'];
          return {
            'name': result['name'] ?? '',
            'address': result['formatted_address'] ?? '',
            'lat': location['lat'].toDouble(),
            'lng': location['lng'].toDouble(),
          };
        }
      }
      return null;
    } catch (e) {
      print('Error getting place details: $e');
      return null;
    }
  }
}

