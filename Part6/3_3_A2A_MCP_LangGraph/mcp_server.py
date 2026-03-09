import os
import requests
import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount

# OpenWeatherMap API 키 확인
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# MCP 서버 객체 생성
mcp = FastMCP("Real-time Weather MCP Server")

# 각 함수는 @mcp.tool() 데코레이터를 사용하여 MCP 서버에 Tool로 등록됩니다.
@mcp.tool()
def get_geocoding(location: str) -> dict:
    """
    사용자 질문에서 지역 이름을 추출하고 해당 장소의 위도 및 경도 정보를 가져옵니다.

    Args:
        location: 지역 이름
    Returns:
        dict: 위도(lat)와 경도(lon)를 담은 딕셔너리
    """
    print(f"[MCP] 좌표 조회 시작: {location}")
    try:
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": location,
            "limit": 1,
            "appid": WEATHER_API_KEY
        }
        response = requests.get(geo_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            result = {
                "lat": data[0]['lat'],
                "lon": data[0]['lon'],
                "name": data[0].get('local_names', {}).get('ko', data[0]['name'])
            }
            print(f"[MCP] API 조회 성공: {result}")
            return result
        else:
            print(f"[MCP] 좌표 정보 없음: {location}")
            return {}
           
    except Exception as e:
        print(f"[MCP] API 조회 실패: {e}")
        return {"error": str(e)}

@mcp.tool()
def get_weather_data(lat: float, lon: float) -> dict:
    """
    좌표의 현재 날씨 정보를 가져옵니다.

    Args:
        lat: 위도
        lon: 경도
    Returns:
        dict: 날씨 정보 (온도, 습도, 날씨 설명 등)
    """
    print(f"[MCP] 날씨 조회 시작: 위도 {lat:.2f}, 경도 {lon:.2f}")
    try:
        weather_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "kr"
        }
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()
        print(f"[MCP] API 날씨 조회 성공")
        return weather_data
    except Exception as e:
        print(f"[MCP] API 날씨 조회 실패: {e}")
        return {"error": str(e)}

http_app = mcp.http_app()
app = Starlette(routes=[Mount("/", app=http_app)], lifespan=http_app.lifespan)

if __name__ == "__main__":
    print(f"🚀 Real-time Weather MCP 서버를 시작합니다.")
    uvicorn.run(app, host="0.0.0.0", port=7000)