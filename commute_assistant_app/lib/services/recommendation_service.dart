import '../models/weather_info.dart';

/// 외부 데이터베이스에서 추천 정보를 가져오는 서비스
/// 사용자가 외부 DB를 연결할 수 있도록 인터페이스 제공
class RecommendationService {
  // 외부 DB 연결을 위한 콜백 함수들
  Function(String condition)? onGetClothing;
  Function(String condition)? onGetBooks;
  Function(String condition)? onGetMusic;

  RecommendationService({
    this.onGetClothing,
    this.onGetBooks,
    this.onGetMusic,
  });

  Future<Recommendation> getRecommendations(String weatherCondition) async {
    // 외부 DB 연결이 설정되어 있으면 사용
    if (onGetClothing != null && onGetBooks != null && onGetMusic != null) {
      try {
        final clothing = await onGetClothing!(weatherCondition);
        final books = await onGetBooks!(weatherCondition);
        final music = await onGetMusic!(weatherCondition);

        return Recommendation(
          clothing: clothing is String ? clothing : clothing.toString(),
          books: books is List<String>
              ? books
              : books is List
                  ? books.map((e) => e.toString()).toList()
                  : [books.toString()],
          music: music is List<String>
              ? music
              : music is List
                  ? music.map((e) => e.toString()).toList()
                  : [music.toString()],
          clothingItems: const [],
        );
      } catch (e) {
        print('Error getting recommendations from external DB: $e');
        // 에러 발생 시 기본 추천 반환
        return _getDefaultRecommendations(weatherCondition);
      }
    }

    // 외부 DB가 연결되지 않았으면 기본 추천 반환
    return _getDefaultRecommendations(weatherCondition);
  }

  Recommendation _getDefaultRecommendations(String condition) {
    switch (condition) {
      case 'rainy':
        return Recommendation(
          clothing: '우산과 레인코트를 준비하세요',
          books: ['비 오는 날 읽기 좋은 소설', '실내에서 즐기는 에세이'],
          music: ['비 오는 날 플레이리스트', '잔잔한 재즈'],
          clothingItems: const [],
        );
      case 'snowy':
        return Recommendation(
          clothing: '따뜻한 코트와 장갑을 착용하세요',
          books: ['겨울 이야기', '따뜻한 감성의 에세이'],
          music: ['겨울 감성 플레이리스트', '따뜻한 발라드'],
          clothingItems: const [],
        );
      case 'cloudy':
        return Recommendation(
          clothing: '가벼운 겉옷을 준비하세요',
          books: ['편안하게 읽는 소설', '인문학 서적'],
          music: ['편안한 인디 음악', '어쿠스틱 플레이리스트'],
          clothingItems: const [],
        );
      default: // sunny
        return Recommendation(
          clothing: '가볍고 시원한 옷을 입으세요',
          books: ['밝은 날 읽기 좋은 소설', '여행 에세이'],
          music: ['밝은 팝 음악', '신나는 댄스 음악'],
          clothingItems: const [],
        );
    }
  }
}

