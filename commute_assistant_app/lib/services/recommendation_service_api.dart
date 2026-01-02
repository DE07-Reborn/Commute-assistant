import '../models/weather_info.dart';
import 'weather_service_api.dart';

/// FastAPI를 통해 추천 정보를 가져오는 서비스
class RecommendationServiceApi {
  final WeatherServiceApi weatherService;
  
  RecommendationServiceApi({
    required this.weatherService,
  });
  
  /// 날씨 조건에 따른 추천 정보 가져오기
  Future<Recommendation> getRecommendations(String weatherCondition, {double? latitude, double? longitude}) async {
    try {
      // 통합 데이터에서 추천 정보 가져오기
      Map<String, dynamic>? unifiedData;
      
      // 좌표가 제공되면 좌표 기반으로 통합 데이터 가져오기
      if (latitude != null && longitude != null) {
        unifiedData = await weatherService.getUnifiedDataByCoordinates(latitude, longitude);
      } else {
        unifiedData = await weatherService.getUnifiedData();
      }
      
      if (unifiedData == null) {
        print('통합 데이터를 가져올 수 없어 기본 추천을 반환합니다.');
        return _getDefaultRecommendations(weatherCondition);
      }
      
      // 도서 정보 추출
      final bookData = unifiedData['book'];
      final books = <String>[];
      final bookLinks = <String>[];
      if (bookData != null) {
        // "(지음)", "(지은이)" 텍스트 제거
        String author = bookData['author']?.toString() ?? '';
        author = author.replaceAll('(지음)', '').replaceAll('(지은이)', '').trim();
        // 제목과 저자를 줄바꿈으로 구분하여 표시
        if (author.isNotEmpty) {
          books.add('${bookData['title']}\n$author');
        } else {
          books.add(bookData['title']?.toString() ?? '');
        }
        // book_link 또는 link 필드에서 링크 추출
        final link = bookData['link'] ?? bookData['book_link'];
        if (link != null && link.toString().trim().isNotEmpty) {
          String linkStr = link.toString().trim();
          // http:// 또는 https://가 없으면 추가하지 않음 (잘못된 링크)
          if (linkStr.startsWith('http://') || linkStr.startsWith('https://')) {
            bookLinks.add(linkStr);
            print('도서 링크 추가: $linkStr');
          } else {
            print('도서 링크 형식이 올바르지 않음: $linkStr');
            bookLinks.add('');  // 링크가 없으면 빈 문자열
          }
        } else {
          print('도서 링크가 없음');
          bookLinks.add('');  // 링크가 없으면 빈 문자열
        }
      }
      
      // 음악 정보 추출
      final musicData = unifiedData['music'] as List<dynamic>?;
      final music = <String>[];
      if (musicData != null && musicData.isNotEmpty) {
        for (var track in musicData) {
          final trackName = track['trackName']?.toString() ?? '';
          final albumName = track['albumName']?.toString() ?? '';
          final artists = (track['artists']?.toString() ?? '').replaceAll(';', ', ');
          // 트랙 네임\n앨범 네임\n아티스트 형식으로 저장
          music.add('$trackName\n$albumName\n$artists');
        }
      }
      
      // 옷차림 추천 (날씨 조건에 따라)
      final clothing = _getClothingRecommendation(weatherCondition);
      
      return Recommendation(
        clothing: clothing,
        books: books.isNotEmpty ? books : _getDefaultBooks(weatherCondition),
        music: music.isNotEmpty ? music : _getDefaultMusic(weatherCondition),
        bookLinks: bookLinks.isNotEmpty ? bookLinks : null,
      );
    } catch (e) {
      print('추천 정보 가져오기 오류: $e');
      return _getDefaultRecommendations(weatherCondition);
    }
  }
  
  String _getClothingRecommendation(String condition) {
    switch (condition) {
      case 'rainy':
        return '우산과 레인코트를 준비하세요';
      case 'snowy':
        return '따뜻한 코트와 장갑을 착용하세요';
      case 'cloudy':
        return '가벼운 겉옷을 준비하세요';
      default: // sunny
        return '가볍고 시원한 옷을 입으세요';
    }
  }
  
  List<String> _getDefaultBooks(String condition) {
    switch (condition) {
      case 'rainy':
        return ['비 오는 날 읽기 좋은 소설', '실내에서 즐기는 에세이'];
      case 'snowy':
        return ['겨울 이야기', '따뜻한 감성의 에세이'];
      case 'cloudy':
        return ['편안하게 읽는 소설', '인문학 서적'];
      default: // sunny
        return ['밝은 날 읽기 좋은 소설', '여행 에세이'];
    }
  }
  
  List<String> _getDefaultMusic(String condition) {
    switch (condition) {
      case 'rainy':
        return ['비 오는 날 플레이리스트', '잔잔한 재즈'];
      case 'snowy':
        return ['겨울 감성 플레이리스트', '따뜻한 발라드'];
      case 'cloudy':
        return ['편안한 인디 음악', '어쿠스틱 플레이리스트'];
      default: // sunny
        return ['밝은 팝 음악', '신나는 댄스 음악'];
    }
  }
  
  Recommendation _getDefaultRecommendations(String condition) {
    return Recommendation(
      clothing: _getClothingRecommendation(condition),
      books: _getDefaultBooks(condition),
      music: _getDefaultMusic(condition),
      bookLinks: null,  // 기본 추천은 링크 없음
    );
  }
}

