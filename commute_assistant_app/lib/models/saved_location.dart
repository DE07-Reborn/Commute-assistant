class SavedLocation {
  final String id;
  final String name;
  final String address;
  final String type; // 'home', 'work', 'favorite'
  final double? lat;
  final double? lng;

  SavedLocation({
    required this.id,
    required this.name,
    required this.address,
    required this.type,
    this.lat,
    this.lng,
  });
}

