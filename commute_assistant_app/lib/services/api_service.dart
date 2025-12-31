import 'dart:convert';
import 'package:http/http.dart' as http;

/// FastAPI 서버와 통신하는 기본 서비스
class ApiService {
  final String baseUrl;
  
  ApiService({required this.baseUrl});
  
  /// GET 요청
  Future<Map<String, dynamic>?> get(String endpoint) async {
    try {
      final url = Uri.parse('$baseUrl$endpoint');
      final response = await http.get(
        url,
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      } else {
        print('API 요청 실패: ${response.statusCode}, URL: $url');
        print('응답 본문: ${response.body}');
        return null;
      }
    } catch (e) {
      print('API 요청 오류: $e');
      return null;
    }
  }
  
  /// POST 요청
  Future<Map<String, dynamic>?> post(String endpoint, Map<String, dynamic> body) async {
    try {
      final url = Uri.parse('$baseUrl$endpoint');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode(body),
      );
      
      if (response.statusCode == 200 || response.statusCode == 201) {
        return json.decode(response.body) as Map<String, dynamic>;
      } else {
        // 에러 응답도 파싱하여 상세 정보 반환
        try {
          final errorData = json.decode(response.body) as Map<String, dynamic>;
          throw Exception(errorData['detail'] ?? '요청 실패');
        } catch (_) {
          throw Exception('요청 실패: ${response.statusCode}');
        }
      }
    } catch (e) {
      print('API POST 요청 오류: $e');
      rethrow;
    }
  }
  
  /// 로그인
  Future<Map<String, dynamic>> login(String username, String password) async {
    final body = {
      'username': username,
      'password': password,
    };
    return await post('/api/v1/auth/login', body) ?? {};
  }
  
  /// 회원가입
  Future<Map<String, dynamic>> signup({
    required String username,
    required String password,
    required String name,
    required String gender,
    required String homeAddress,
    required String workAddress,
    required String workStartTime,
  }) async {
    final body = {
      'username': username,
      'password': password,
      'name': name,
      'gender': gender,
      'home_address': homeAddress,
      'work_address': workAddress,
      'work_start_time': workStartTime,
    };
    return await post('/api/v1/auth/signup', body) ?? {};
  }
}

