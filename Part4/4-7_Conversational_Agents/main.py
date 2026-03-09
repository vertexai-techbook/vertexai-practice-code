import functions_framework
from google import genai
from google.genai import types
import json

@functions_framework.http
def restaurant_recommendation(request):
    payload = request.get_json(silent=True)

    print(payload)
   
    cuisine = payload.get("cuisine")
    location = payload.get("location")

    info = f"{cuisine},{location}"

    si = """
    당신은 AI 기반 레스토랑 추천 어시스턴트입니다.
    선호하는 요리와 위치 정보를 바탕으로, 어시스턴트는 Google 검색 도구를 호출하여 최소 2개에서 최대 5개의 레스토랑을 추천해야 합니다.
    어시스턴트는 레스토랑 이름과 주소, 대표 메뉴와 평점, 한 줄 요약이 포함된 결과를 반환해야 합니다.
    최종 출력은 유효한 JSON 배열 형식이어야 합니다. JSON 배열 앞뒤에 다른 텍스트나 설명을 포함하지 마세요.
    JSON 스키마는 아래 <SCHEMA>를 참조하십시오.

    <SCHEMA>
    [
    {
        "name": “레스토랑 이름",
        "address": "레스토랑 주소",
        "menu": "레스토랑 시그니처 메뉴",
        "rating": "레스토랑 평점",
        "summary": "레스토랑 요약"
    },
    ...
    ]
    </SCHEMA>

    """

    tools = [types.Tool(google_search=types.GoogleSearch())]

    client = genai.Client(vertexai=True, project="vertexai-books", location="asia-northeast3")    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=info,
        config=types.GenerateContentConfig(
            temperature=0,
            system_instruction=si,
            tools=tools,
        )
    )

    raw_text = response.text
    if raw_text.strip().startswith("```json"):
        cleaned_text = '\n'.join(raw_text.strip().split('\n')[1:-1])
    else:
        cleaned_text = raw_text

    parsed_result = json.loads(cleaned_text)
    print(f"추천 결과: {json.dumps(parsed_result, indent=2, ensure_ascii=False)}")
    return parsed_result