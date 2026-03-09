# == 1. Code Execution == #
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="vertexai-books", location="global")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="1부터 100까지의 수 중 모든 소수의 합, 곱은 뭔가요? 각각 계산하는 코드를 생성하고 실행하여 결과를 알려주세요.",
    config=types.GenerateContentConfig(
        tools=[types.Tool(code_execution=types.ToolCodeExecution)]
    ),
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(f"### 응답 텍스트:\n{part.text}")
    if part.executable_code is not None:
        print(f"### 생성한 코드:\n{part.executable_code.code}")
    if part.code_execution_result is not None:
        print(f"### 실행 결과:\n{part.code_execution_result.output}")
    
# == 2. URL Context == #
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, UrlContext

client = genai.Client(vertexai=True, project="vertexai-books", location="global")
model_id = "gemini-2.5-flash"

tools = []
tools.append(Tool(url_context=UrlContext))
tools.append(Tool(google_search=GoogleSearch))

response = client.models.generate_content(
    model=model_id,
    contents="https://therecipecritic.com/tbone-steak/과 https://www.billyparisi.com/t-bone-steak-with-lemon-butter-and-salted-baked-potato/ 링크에 있는 레시피 두 개 비교해서 어떤 차이점이 있는지 알려줘.",
    config=GenerateContentConfig(
        tools=tools,
        response_modalities=["TEXT"],
    )
)

for each in response.candidates[0].content.parts:
    print(f"### 응답 텍스트:\n{each.text}")

print(f"### 응답 메타데이터:\n{response.candidates[0].url_context_metadata}")    

# == 3. Google Search == #
from google import genai

client = genai.Client(vertexai=True, project="vertexai-books", location="global")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="24-25 챔피언스리그 우승팀 알려줘.",
)

print(response.text)

from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="vertexai-books", location="global")

tools = [types.Tool(google_search=types.GoogleSearch())]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="24-25 챔피언스리그 우승팀 알려줘.",
    config=types.GenerateContentConfig(
        tools = tools
    )
)

print(response.text)

# 응답 본문 내 인용으로 출처 표시하기
def add_citations(response):
    text = response.text
    supports = response.candidates[0].grounding_metadata.grounding_supports
    chunks = response.candidates[0].grounding_metadata.grounding_chunks

    # end_index 내림차순으로 정렬
    sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

    for support in sorted_supports:
        end_index = support.segment.end_index
        if support.grounding_chunk_indices:
            # [1](link1)[2](link2)의 형태로 인용 생성
            citation_links = []
            for i in support.grounding_chunk_indices:
                if i < len(chunks):
                    uri = chunks[i].web.uri
                    citation_links.append(f"[{i + 1}]({uri})")

            citation_string = ", ".join(citation_links)
            text = text[:end_index] + citation_string + text[end_index:]

    return text

text_with_citations = add_citations(response)
print(text_with_citations)

# == 4. Google Maps == #
from google import genai
from google.genai import types
import base64
import os

client = genai.Client(vertexai=True,project="vertexai-books", location="global")

tools = [types.Tool(google_maps=types.GoogleMaps())]
generate_content_config = types.GenerateContentConfig(
    tools = tools,
    system_instruction="당신은 전세계 모든 맛집을 알고 있는 맛집 전문가입니다. 맛집 주소와 함께 어떤 음식을 팔고 평점과 평이 어떤지 간단히 요약하여 Google Maps 링크와 함께 제공해야 합니다."
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="시드니 CBD에 있는 서비스 좋고 평 좋은 음식점 3곳 정도만 추천해줘.",
    config=generate_content_config
)

print(response.text)

from google import genai
from google.genai import types
import base64
import os

client = genai.Client(vertexai=True,project="vertexai-books", location="asia-northeast3")

tools = [types.Tool(google_maps=types.GoogleMaps())]
tool_config = types.ToolConfig(
    retrieval_config = types.RetrievalConfig(
    lat_lng = types.LatLng(
        latitude=37.503394,
        longitude=126.881399 # 내 현재 위치의 위도, 경도 정보를 입력
    ),
    language_code = "ko_KR"
    ),
)


generate_content_config = types.GenerateContentConfig(
    tools = tools,
    tool_config = tool_config,
    system_instruction="당신은 전세계 모든 맛집을 알고 있는 맛집 전문가입니다. 맛집 주소와 함께 어떤 음식을 팔고 평점과 평이 어떤지 간단히 요약하여 Google Maps 링크와 함께 제공해야 합니다."
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="지금 내가 있는 곳 근처에 있는 음식점 3개만 찾아줄 수 있어?",
    config=generate_content_config
)

print(response.text)