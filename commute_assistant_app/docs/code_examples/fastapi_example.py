"""
FastAPI 서버 예시
Redis에서 데이터를 조회하여 Flutter 앱에 제공
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import redis
import json
from datetime import datetime

app = FastAPI(title="Commute Assistant API", version="1.0.0")

# CORS 설정 (Flutter 앱에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis 연결 (환경 변수 사용)
import os

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    db=int(os.getenv('REDIS_DB', '0')),
    password=os.getenv('REDIS_PASSWORD', None),
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


class BookInfo(BaseModel):
    title: str
    author: str
    link: Optional[str] = None


class MusicTrack(BaseModel):
    trackName: str
    artists: str
    albumName: str


class RecommendationResponse(BaseModel):
    books: list[BookInfo]
    music: list[MusicTrack]


# Redis 서비스
class RedisService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def get_weather_data(self, station_id: str) -> Optional[dict]:
        """날씨 데이터 조회"""
        key = f"kma-stn:{station_id}"
        data = self.redis.hgetall(key)
        if not data:
            return None
        
        # Redis Hash를 dict로 변환
        return {
            'temperature': float(data.get('ta', 0)),
            'condition': self._map_weather_condition(data.get('wc', '')),
            'humidity': int(data.get('hm', 0)),
            'windSpeed': float(data.get('ws', 0)),
            'description': self._get_description(data.get('wc', '')),
            'location': data.get('location', '서울시 강남구')
        }
    
    def get_book_recommendations(self, weather_condition: str) -> list[dict]:
        """도서 추천 조회"""
        key = f"book:{weather_condition}"
        data = self.redis.hgetall(key)
        
        if not data:
            return []
        
        return [{
            'title': data.get('book_title', ''),
            'author': data.get('book_author', ''),
            'link': data.get('book_link', None)
        }]
    
    def get_music_recommendations(self, weather_condition: str) -> list[dict]:
        """음악 추천 조회"""
        key = f"music:{weather_condition}"
        # Redis List에서 JSON 문자열로 저장된 경우
        data_list = self.redis.lrange(key, 0, -1)
        
        music_tracks = []
        for item in data_list:
            try:
                track = json.loads(item)
                music_tracks.append({
                    'trackName': track.get('track_name', ''),
                    'artists': track.get('artists', ''),
                    'albumName': track.get('album_name', '')
                })
            except json.JSONDecodeError:
                continue
        
        return music_tracks
    
    def _map_weather_condition(self, wc: str) -> str:
        """날씨 카테고리를 condition으로 매핑"""
        condition_map = {
            '화창': 'sunny',
            '흐림': 'cloudy',
            '비': 'rainy',
            '눈': 'snowy'
        }
        return condition_map.get(wc, 'sunny')
    
    def _get_description(self, wc: str) -> str:
        """날씨 카테고리를 설명으로 변환"""
        desc_map = {
            '화창': '맑음',
            '흐림': '흐림',
            '비': '비',
            '눈': '눈'
        }
        return desc_map.get(wc, '맑음')


# 의존성 주입
def get_redis_service() -> RedisService:
    return RedisService(redis_client)


# API 엔드포인트
@app.get("/api/v1/weather/{station_id}", response_model=WeatherInfo)
async def get_weather(
    station_id: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """날씨 데이터 조회"""
    weather_data = redis_service.get_weather_data(station_id)
    
    if not weather_data:
        raise HTTPException(
            status_code=404,
            detail=f"Station {station_id}의 날씨 데이터를 찾을 수 없습니다"
        )
    
    return WeatherInfo(**weather_data)


@app.get("/api/v1/recommendations/books", response_model=RecommendationResponse)
async def get_book_recommendations(
    weather_condition: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """도서 추천 조회"""
    books = redis_service.get_book_recommendations(weather_condition)
    
    return RecommendationResponse(
        books=[BookInfo(**book) for book in books],
        music=[]
    )


@app.get("/api/v1/recommendations/music", response_model=RecommendationResponse)
async def get_music_recommendations(
    weather_condition: str,
    redis_service: RedisService = Depends(get_redis_service)
):
    """음악 추천 조회"""
    music = redis_service.get_music_recommendations(weather_condition)
    
    return RecommendationResponse(
        books=[],
        music=[MusicTrack(**track) for track in music]
    )


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

