import 'package:redis/redis.dart';
import 'dart:convert';

/// Redis 서비스 클래스
/// 로컬 Docker 컨테이너의 Redis에 연결하여 날씨 데이터를 가져옵니다
class RedisService {
  Command? _command;
  final String _host;
  final int _port;
  final String? _password;
  bool _isConnected = false;

  RedisService({
    String host = 'localhost',
    int port = 6379,
    String? password,
  })  : _host = host,
        _port = port,
        _password = password;

  /// Redis 연결
  Future<void> connect() async {
    try {
      final conn = RedisConnection();
      _command = await conn.connect(_host, _port);
      
      if (_password != null && _password.isNotEmpty) {
        final cmd = _command;
        if (cmd != null) {
          await cmd.send_object(['AUTH', _password]);
        }
      }
      _isConnected = true;
      print('Redis 연결 성공: $_host:$_port');
    } catch (e) {
      _isConnected = false;
      print('Redis 연결 실패: $e');
      rethrow;
    }
  }

  /// Redis 연결 해제
  Future<void> disconnect() async {
    if (_isConnected && _command != null) {
      // Command 객체는 연결을 직접 닫을 수 없으므로
      // 연결이 자동으로 닫히도록 합니다
      _isConnected = false;
      _command = null;
      print('Redis 연결 해제');
    }
  }

  /// Redis에서 날씨 데이터 가져오기
  /// 
  /// [key] Redis 키 (예: 'weather:latest', 'weather:90' 등)
  /// 
  /// 반환값: Map<String, dynamic> 형태의 날씨 데이터
  /// - ws: 풍속 (double)
  /// - ta: 기온 (double)
  /// - hm: 습도 (int)
  /// - wc: 날씨 카테고리 (String, 예: '화창', '흐림')
  Future<Map<String, dynamic>?> getWeatherData(String key) async {
    if (!_isConnected || _command == null) {
      await connect();
    }

    if (_command == null) {
      return null;
    }

    try {
      // Redis에서 데이터 가져오기
      // Hash 형태로 저장된 경우
      final command = await _command!.send_object(['HGETALL', key]);
      
      if (command is List && command.isNotEmpty) {
        // Hash 데이터를 Map으로 변환
        final Map<String, dynamic> data = {};
        for (int i = 0; i < command.length; i += 2) {
          if (i + 1 < command.length) {
            final field = command[i].toString();
            final value = command[i + 1].toString();
            data[field] = value;
          }
        }
        return data;
      }

      // JSON 문자열로 저장된 경우
      final jsonCommand = await _command!.send_object(['GET', key]);
      if (jsonCommand != null) {
        final jsonString = jsonCommand.toString();
        if (jsonString.startsWith('{') || jsonString.startsWith('[')) {
          return json.decode(jsonString) as Map<String, dynamic>;
        }
      }

      return null;
    } catch (e) {
      print('Redis 데이터 가져오기 실패: $e');
      return null;
    }
  }

  /// Redis에서 특정 필드 값 가져오기 (Hash)
  Future<String?> getHashField(String key, String field) async {
    if (!_isConnected || _command == null) {
      await connect();
    }

    if (_command == null) {
      return null;
    }

    try {
      final result = await _command!.send_object(['HGET', key, field]);
      return result?.toString();
    } catch (e) {
      print('Redis Hash 필드 가져오기 실패: $e');
      return null;
    }
  }

  /// Redis에서 키 목록 가져오기 (패턴 매칭)
  Future<List<String>> getKeys(String pattern) async {
    if (!_isConnected || _command == null) {
      await connect();
    }

    if (_command == null) {
      return [];
    }

    try {
      final result = await _command!.send_object(['KEYS', pattern]);
      if (result is List) {
        return result.map((e) => e.toString()).toList();
      }
      return [];
    } catch (e) {
      print('Redis 키 목록 가져오기 실패: $e');
      return [];
    }
  }

  /// 연결 상태 확인
  bool get isConnected => _isConnected;
}

