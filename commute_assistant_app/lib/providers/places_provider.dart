import 'package:flutter/foundation.dart';
import '../services/places_service.dart';

class PlacesProvider with ChangeNotifier {
  final PlacesService _placesService;

  PlacesProvider({required PlacesService placesService})
      : _placesService = placesService;

  PlacesService get placesService => _placesService;
}

