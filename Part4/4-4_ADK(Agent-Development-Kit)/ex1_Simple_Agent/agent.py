import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

# 도구1. 특정 도시의 날씨 정보를 가져옵니다.
def get_weather(city: str) -> dict:
    """특정 도시의 현재 날씨 정보를 검색합니다.
    Args:
        city (str): 날씨 정보를 검색할 도시 이름
    Returns:
        dict: 검색 결과
    """
    if city.lower() == "서울":
        return {
            "status": "success",
            "report": (
                "서울의 날씨는 맑고 기온은 25도 입니다."
                "섭씨 기준.(화씨 77도)"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"'{city}' 도시의 날씨는 검색할 수 없습니다."
        }

# 도구2. 특정 도시의 현재 시간을 가져옵니다.
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.
    Args:
        city (str): 현재 시간을 검색할 도시 이름
    Returns:
        dict: 검색 결과
    """
    if city.lower() == "서울":
        tz_identifier = "Asia/Seoul"
    else:
        return {
            "status": "error",
            "error_message": (
                f"{city} 도시의 현재 시간을 가져올 수 없습니다."
            ),
        }
    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'{city} 도시의 현재 시간은 {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")} 입니다.'
    )
    return {"status": "success", "report": report}

# LlmAgent 정의
root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.5-flash", # 사용할 Gemini 모델 지정
    description="도시의 실시간 날씨 및 시간을 조회할 수 있는 에이전트입니다.",
    instruction=(
        "당신은 사용자에의 질문에서 도시를 식별하고, 해당 도시의 실시간 날씨 및 시간을 조회할 수 있는 에이전트입니다."
        "사용자가 날씨를 물어보는 경우, 'get_weather' 도구를 호출하여 검색하고, 현재 시간을 물어보는 경우 'get_current_time' 도구를 호출하여 조회하세요."
    ),
    tools=[get_weather, get_current_time], # 에이전트가 사용할 도구 목록
)