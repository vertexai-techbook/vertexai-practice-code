# == 2.1. 함수 선언 == #
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="vertexai-books", location="global")

get_landmarks_function = {
    "name": "get_landmarks",
    "description": "주어진 지역의 랜드마크 정보를 가져옵니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "도시 이름 (예: 서울, 뉴욕)",
            },        
        },
        "required": ["location"],
    },
}

def get_landmarks(location) -> str:
    """Get information about landmarks.
 
    Args:
        location: 지역 이름
 
    Returns:
        랜드마크의 한 줄 요약
    """
   
    if location == "서울":
        # 예제를 위한 Dummy 데이터 반환
        return {"name": "경복궁", "summary": "조선 왕조 제일의 법궁"}
    else:
        return {"name": "정보 없음", "summary": "해당 위치의 랜드마크 정보가 없습니다."}

tools = types.Tool(function_declarations=[get_landmarks_function])
config = types.GenerateContentConfig(tools=[tools])

# == 2.2. 모델의 판단 == #
contents = [
    types.Content(
        role="user", parts=[types.Part(text="서울의 랜드마크 알려줘.")]
    )
]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=config,
)

# Gemini 응답에서 함수 호출 체크
tool_call = response.candidates[0].content.parts[0].function_call
if tool_call:
    print(f"Function: {tool_call.name}")
    print(f"Arguement: {tool_call.args}")
else:
    print("응답에서 함수가 호출되지 않았습니다.")
    print(response.text)

# == 2.3. 함수 실행 == #
if tool_call.name == "get_landmarks":
    result = get_landmarks(**tool_call.args)
    print(f"Result: {result}")

# == 2.4. 결과 전달 및 최종 답변 생성 == #
    # 함수 응답 부분 직접 만들기
    function_response_part = types.Part.from_function_response(
        name=tool_call.name,
        response={"Result": result},
    )


    # 함수 호출 및 함수 실행 결과를 콘텐츠에 직접 추가
    contents.append(response.candidates[0].content)
    contents.append(types.Content(role="user", parts=[function_response_part]))


    final_response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=config,
        contents=contents,
    )

    print(final_response.text)

# == 3.2. 자동 함수 호출(Only Python) == #
def get_landmarks(location: str) -> dict:
    """
    사용자 질문에서 지역 이름을 추출하고 해당 지역의 랜드마크 정보를 반환합니다.


    Args:
        location: 지역 이름


    Returns:
        랜드마크 이름 및 한 줄 요약
    """
    if location == "서울":
        # 예제를 위한 Dummy 데이터 반환
        return {"name": "경복궁", "summary": "조선 왕조 제일의 법궁"}
    else:
        return {"name": "정보 없음", "summary": "해당 지역의 랜드마크 정보가 없습니다."}

config = types.GenerateContentConfig(tools=[get_landmarks])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="서울의 랜드마크 알려줘.",
    config=config,
)

print(response.text)

# == 4. 병렬 함수 호출 == #
# 실제 함수 구현
def brew_coffee(strength: str) -> dict:
    """
    지정된 농도로 커피를 내립니다.


    Args:
        strength: 커피 농도 ('진하게' 또는 '부드럽게')


    Returns:
        status: 현재 커피 상태를 나타냅니다.
    """
    return {"status": f"{strength} 커피를 내리고 있습니다."}


def get_daily_briefing(topics: list[str] = ["news", "weather"]) -> dict:
    """
    지정된 주제에 대한 일일 브리핑을 가져옵니다.


    Args:
        topics: 브리핑에 포함할 주제 목록


    Returns:
        briefing_topics: 브리핑 주제
    """
    return {"briefing_topics": topics}


def set_thermostat(temperature_celsius: float = 22.0) -> dict:
    """
    실내 온도를 조절합니다.


    Args:
        temperature_celsius: 목표 온도 (섭씨)


    Returns:
        temperature: 온도 설정값.
    """
    return {"temperature": f"{temperature_celsius}°C"}

config = types.GenerateContentConfig(
    system_instruction="사용자의 모닝 루틴을 위해 필요한 모든 도구를 호출하세요.",
    tools=[brew_coffee, get_daily_briefing, set_thermostat]
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="좋은 아침! 하루를 시작할 준비를 해줘. 커피는 부드럽게~",
    config=config,
)

print(response.text)

# == 5. 순차 함수 호출 == #
import requests

API_KEY = "<OpenWeatherMap API KEY>"

def get_geocoding(location: str) -> dict | None:
    """
    사용자 질문에서 지역 이름을 추출하고 해당 장소의 위도 및 경도 정보를 가져옵니다.


    Args:
        location: 지역 이름


    Returns:
        lat: 지역의 위도
        lon: 지역의 경도
    """
    # Geocoding API URL
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"


    # API 요청에 필요한 파라미터
    params = {
        "q": location,
        "limit": 1,
        "appid": API_KEY
    }


    print(f"1. 도시 '{location}'의 좌표를 조회합니다...")
    try:
        response = requests.get(geo_url, params=params)
        response.raise_for_status()
       
        data = response.json()
        lat = data[0]['lat']
        lon = data[0]['lon']
        return {"lat": lat, "lon": lon}


    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}")
        return None, None
   
def get_weather_data(lat: float, lon: float) -> dict | None:
    """
    위도와 경도를 사용하여 현재 날씨를 조회합니다.


    Args:
        lat: 지역의 위도
        lon: 지역의 경도


    Returns:
        current_weather: 지역의 현재 날씨
    """
    # Current Weather API URL
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
   
    # API 요청에 필요한 파라미터
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",  # 온도를 섭씨(°C)로 받기
        "lang": "kr"        # 응답을 한국어로 받기
    }
   
    print("\n2. 해당 좌표의 현재 날씨를 조회합니다...")
    try:
        response = requests.get(weather_url, params=params)
        response.raise_for_status()
       
        weather_data = response.json()
        return {"current_weather": weather_data}


    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}")
        return None


config = types.GenerateContentConfig(
    tools=[get_geocoding, get_weather_data]
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="서울의 현재 날씨 알려줘.",
    config=config,
)

print(response.text)

# == 6. Function Calling 모드 == #
# Function Calling 모드 설정
tool_config = types.ToolConfig(
    function_calling_config=types.FunctionCallingConfig(
        mode="ANY",
        allowed_function_names=["<함수 이름>"] # NONE일 땐 allowed_function_names 필드는 설정이 불가합니다.


    )
)

# 생성 구성 생성
config = types.GenerateContentConfig(
    tools=[tools],
    tool_config=tool_config,
)

# 함수 호출 결과 확인
for part in response.candidates[0].content.parts:
    if part.function_call:
        fc = part.function_call
        print(f"함수: {fc.name}, 인자: {fc.args}")

config = types.GenerateContentConfig(
    system_instruction="사용자의 모닝 루틴을 위해 필요한 모든 도구를 호출하세요.",
    tools=[brew_coffee, get_daily_briefing, set_thermostat],
    tool_config = types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(
            mode="ANY",
            allowed_function_names=["brew_coffee", "get_daily_briefing", "set_thermostat"]
        )
    )

)

# 1. 첫 번째 요청
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="좋은 아침! 하루를 시작할 준비를 해줘. 커피는 부드럽게~",
    config=config,
)

# 2. 함수 실행 및 결과 수집
function_map = {
    "brew_coffee": brew_coffee,
    "get_daily_briefing": get_daily_briefing,
    "set_thermostat": set_thermostat,
}

function_responses = []
for part in response.candidates[0].content.parts:
    if part.function_call:
        fc = part.function_call
        result = function_map[fc.name](**fc.args)
        function_responses.append(
            types.Part.from_function_response(name=fc.name, response=result)
        )


# 3. 함수 결과를 모델에 전달하여 최종 응답 받기
final_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Content(role="user", parts=[types.Part(text="좋은 아침! 하루를 시작할 준비를 해줘. 커피는 부드럽게~")]),
        response.candidates[0].content,  # 모델의 함수 호출
        types.Content(role="user", parts=function_responses),  # 함수 실행 결과
    ],
    config=types.GenerateContentConfig(
        system_instruction="사용자의 모닝 루틴을 위해 필요한 도구들을 호출해야 합니다.",
        tools=[brew_coffee, get_daily_briefing, set_thermostat],
    ),
)

print(final_response.text)  # 이제 텍스트 응답이 나옵니다
