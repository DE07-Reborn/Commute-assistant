"""
Google Maps API를 사용한 주소 검증 및 좌표 변환
"""
import os
import httpx
from typing import Optional, Dict


class AddressService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    async def validate_and_get_coordinates(self, address: str) -> Optional[Dict[str, str]]:
        """
        주소를 검증하고 좌표를 가져옴
        
        Returns:
            {
                'formatted_address': str,
                'latitude': str,
                'longitude': str
            } 또는 None
        """
        if not address or not address.strip():
            print("주소가 비어있습니다")
            return None
            
        if not self.api_key or not self.api_key.strip():
            print(f"Google Maps API 키가 설정되지 않았습니다 (키 길이: {len(self.api_key) if self.api_key else 0})")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Geocoding API로 주소 검증 및 좌표 변환
                url = f"{self.base_url}/geocode/json"
                params = {
                    "address": address,
                    "key": self.api_key,
                    "language": "ko",
                    "region": "kr"
                }
                
                print(f"주소 검증 요청: {address}")
                response = await client.get(url, params=params)
                data = response.json()
                
                print(f"Google Maps API 응답 상태: {data.get('status')}")
                
                if data.get("status") == "OK" and data.get("results"):
                    result = data["results"][0]
                    location = result["geometry"]["location"]
                    
                    # 사용자가 입력한 원본 주소를 우선 사용 (API가 반환한 주소와 다를 수 있음)
                    formatted_address = address
                    
                    print(f"주소 검증 성공: 원본 주소={address}, API 반환 주소={result.get('formatted_address', '')}")
                    return {
                        "formatted_address": formatted_address,
                        "latitude": str(location["lat"]),
                        "longitude": str(location["lng"])
                    }
                elif data.get("status") == "ZERO_RESULTS":
                    print(f"주소를 찾을 수 없음: {address}")
                    return None
                elif data.get("status") == "REQUEST_DENIED":
                    error_message = data.get("error_message", "API 요청이 거부되었습니다")
                    print(f"API 요청 거부: {error_message}")
                    return None
                else:
                    print(f"주소 검증 실패: 상태={data.get('status')}, 주소={address}, 응답={data}")
                    return None
                    
        except httpx.TimeoutException:
            print(f"주소 검증 타임아웃: {address}")
            return None
        except Exception as e:
            print(f"주소 검증 오류: {type(e).__name__}: {e}, 주소: {address}")
            import traceback
            traceback.print_exc()
            return None
    
    async def autocomplete_address(self, input_text: str) -> list:
        """
        주소 자동완성
        
        Returns:
            [{
                'place_id': str,
                'description': str,
                'main_text': str,
                'secondary_text': str
            }]
        """
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/place/autocomplete/json"
                params = {
                    "input": input_text,
                    "key": self.api_key,
                    "language": "ko",
                    "components": "country:kr"
                }
                
                response = await client.get(url, params=params)
                data = response.json()
                
                if data.get("status") in ["OK", "ZERO_RESULTS"]:
                    predictions = data.get("predictions", [])
                    results = []
                    for pred in predictions:
                        structured = pred.get("structured_formatting", {})
                        results.append({
                            "place_id": pred.get("place_id", ""),
                            "description": pred.get("description", ""),
                            "main_text": structured.get("main_text", ""),
                            "secondary_text": structured.get("secondary_text", "")
                        })
                    return results
                return []
                
        except Exception as e:
            print(f"주소 자동완성 오류: {e}")
            return []

