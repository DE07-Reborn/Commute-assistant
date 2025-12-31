"""
FastAPI 통합 엔드포인트
Redis에 저장된 통합 테이블(날씨 + 도서 + 음악)에서 모든 데이터를 한 번에 조회
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import redis
import json

app = FastAPI(title="Commute Assistant API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis 연결
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)


# Pydantic 모델
class WeatherInfo(BaseModel):
    temperature: float
    condition: str
    humidity: int
    windSpeed: float
    description: str
    location: Optional[str] = None
    uvIndex: Optional[str] = None
    weatherCategory: Optional[str] = None


class BookInfo(BaseModel):
    title: str
    author: str
    link: Optional[str] = None


class MusicTrack(BaseModel):
    trackName: str
    artists: str
    albumName: str


class UnifiedDataResponse(BaseModel):
    """통합 데이터 응답 모델"""
    weather: WeatherInfo
    book: Optional[BookInfo] = None
    music: List[MusicTrack] = []


# Redis 서비스
class RedisService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get_unified_data(self, station_id: str) -> Optional[dict]:
        """
        Redis에서 통합 데이터 조회
        하나의 Hash에 날씨, 도서, 음악 데이터가 모두 저장되어 있음
        """
        key = f"kma-stn:{station_id}"  # 또는 사용자가 사용하는 키 형식
        
        # Hash로 저장된 경우
        data = self.redis.hgetall(key)
        
        if not data:
            return None
        
        return data
    
    def parse_weather_data(self, data: dict) -> dict:
        """날씨 데이터 파싱"""
        # 날씨 카테고리에서 condition 추출
        weather_category = data.get('weather_category', '')
        if '-' in weather_category:
            wc = weather_category.split('-')[-1]
        else:
            wc = weather_category
        
        condition = self._map_weather_condition(wc)
        
        return {
            'temperature': float(data.get('ta', 0)),
            'condition': condition,
            'humidity': int(float(data.get('hm', 0))),
            'windSpeed': float(data.get('ws', 0)),
            'description': wc,
            'location': data.get('location', '서울시 강남구'),
            'uvIndex': data.get('uvIndex'),
            'weatherCategory': wc
        }
    
    def parse_book_data(self, data: dict) -> Optional[dict]:
        """도서 데이터 파싱"""
        book_title = data.get('book_title')
        if not book_title or book_title == '':
            return None
        
        return {
            'title': book_title,
            'author': data.get('book_author', '저자 정보 없음'),
            'link': data.get('book_link') if data.get('book_link') else None
        }
    
    def parse_music_data(self, data: dict) -> List[dict]:
        """음악 데이터 파싱"""
        music_data = data.get('music')
        if not music_data:
            return []
        
        music_tracks = []
        
        # JSON 문자열인 경우
        if isinstance(music_data, str):
            try:
                music_list = json.loads(music_data)
                if isinstance(music_list, list):
                    for item in music_list:
                        if isinstance(item, dict):
                            music_tracks.append({
                                'trackName': item.get('track_name') or item.get('trackName', ''),
                                'artists': item.get('artists', ''),
                                'albumName': item.get('album_name') or item.get('albumName', '')
                            })
            except json.JSONDecodeError:
                pass
        
        # 이미 리스트인 경우
        elif isinstance(music_data, list):
            for item in music_data:
                if isinstance(item, dict):
                    music_tracks.append({
                        'trackName': item.get('track_name') or item.get('trackName', ''),
                        'artists': item.get('artists', ''),
                        'albumName': item.get('album_name') or item.get('albumName', '')
                    })
        
        return music_tracks
    
    def _map_weather_condition(self, wc: str) -> str:
        """날씨 카테고리를 condition으로 매핑"""
        wc_lower = wc.lower()
        if '비' in wc_lower or 'rain' in wc_lower:
            return 'rainy'
        elif '눈' in wc_lower or 'snow' in wc_lower:
            return 'snowy'
        elif '흐림' in wc_lower or 'cloud' in wc_lower:
            return 'cloudy'
        elif '맑음' in wc_lower or '화창' in wc_lower or 'sunny' in wc_lower or 'clear' in wc_lower:
            return 'sunny'
        else:
            return 'sunny'  # 기본값


# 의존성 주입
def get_redis_service() -> RedisService:
    return RedisService(redis_client)


# 통합 API 엔드포인트
@app.get("/api/v1/data/{station_id}", response_model=UnifiedDataResponse)
async def get_unified_data(
    station_id: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    통합 데이터 조회
    Redis의 하나의 테이블에서 날씨, 도서, 음악 데이터를 모두 가져옴
    """
    # Redis에서 통합 데이터 조회
    raw_data = redis_service.get_unified_data(station_id)
    
    if not raw_data:
        raise HTTPException(
            status_code=404,
            detail=f"Station {station_id}의 데이터를 찾을 수 없습니다"
        )
    
    # 데이터 파싱
    weather_data = redis_service.parse_weather_data(raw_data)
    book_data = redis_service.parse_book_data(raw_data)
    music_data = redis_service.parse_music_data(raw_data)
    
    return UnifiedDataResponse(
        weather=WeatherInfo(**weather_data),
        book=BookInfo(**book_data) if book_data else None,
        music=[MusicTrack(**track) for track in music_data]
    )


# 개별 엔드포인트 (기존 호환성 유지)
@app.get("/api/v1/weather/{station_id}", response_model=WeatherInfo)
async def get_weather(
    station_id: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """날씨 데이터만 조회"""
    raw_data = redis_service.get_unified_data(station_id)
    
    if not raw_data:
        raise HTTPException(
            status_code=404,
            detail=f"Station {station_id}의 날씨 데이터를 찾을 수 없습니다"
        )
    
    weather_data = redis_service.parse_weather_data(raw_data)
    return WeatherInfo(**weather_data)


@app.get("/health")
async def health_check():
    """헬스 체크"""
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

