# == 2. 모델 호출 == #
# Gemini 네이티브 방식
from google import genai

client = genai.Client(vertexai=True, project="vertexai-books", location="global")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="LLM은 어떻게 작동하나요? 2줄로 요약해줘"
)
print(response.text)

# OpenAI 호환성 방식
from openai import OpenAI

client = OpenAI(
    api_key="<API Key>",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "user", "content": "LLM은 어떻게 작동하나요? 2줄로 요약해줘"}
    ]
)

print(response.choices[0].message.content)

# == 3. 시스템 지시사항 및 파라미터 설정 == #
# Gemini 네이티브 방식
from google.genai import types

response = client.models.generate_content(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction="당신은 기발하고 엉뚱한 아이디어를 내는 마케팅 전문가입니다.",
    ),
    contents="세상에 존재하지 않는 '매운맛 아이스크림'의 브랜드 이름과 슬로건을 3개만 지어줘."
)
print(response.text)

# OpenAI 호환성 방식
response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": "당신은 기발하고 엉뚱한 아이디어를 내는 마케팅 전문가입니다."},
        {"role": "user", "content": "세상에 존재하지 않는 '매운맛 아이스크림'의 브랜드 이름과 슬로건을 3개만 지어줘."}
    ],
    temperature=0.9,
    top_p=0.9,
    max_tokens=2048
)

print(response.choices[0].message.content)

# == 4. 멀티모달 입력 == #
# Gemini 네이티브 방식
from PIL import Image

# 이미지 파일 경로 지정
image = Image.open("instrument.png")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[image, "사진의 악기는 몇 개이고, 모두 같은 종류의 악기 인가요?"]
)
print(response.text)

# OpenAI 호환성 방식
import base64

# 이미지를 Base64로 인코딩
with open("instrument.png", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')


response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "사진의 악기는 몇 개이고, 모두 같은 종류의 악기인가요?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_data}"
                    }
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)

# == 5. 스트리밍 응답 == #
# Gemini 네이티브 방식
response_stream = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="우주 여행에 대한 짧은 이야기를 써주세요."
)


for chunk in response_stream:
    print(chunk.text, end="")

# OpenAI 호환성 방식
stream = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "user", "content": "우주 여행에 대한 짧은 이야기를 써주세요."}
    ],
    stream=True
)


for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")

# == 6. 멀티-턴(Multi-turn) 구현 == #
# Gemini 네이티브 방식
chat = client.chats.create(model="gemini-2.5-flash")

response1 = chat.send_message("우리 집에 강아지가 2마리 있어.")
print(f"답변 1: {response1.text}")

response2 = chat.send_message("그럼 우리 집엔 발바닥이 모두 몇 개일까?")
print(f"답변 2: {response2.text}")

# OpenAI 호환성 방식
messages = []

# 첫 번째 대화
messages.append({"role": "user", "content": "우리 집에 강아지가 2마리 있어."})
response1 = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=messages
)
assistant_reply1 = response1.choices[0].message.content
messages.append({"role": "assistant", "content": assistant_reply1})
print(f"답변 1: {assistant_reply1}")

# 두 번째 대화
messages.append({"role": "user", "content": "그럼 우리 집엔 발바닥이 모두 몇 개일까?"})
response2 = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=messages
)
assistant_reply2 = response2.choices[0].message.content
print(f"답변 2: {assistant_reply2}")

# == 7. 구조화된 출력 == #
# Gemini 네이티브 방식
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="초코칩 쿠키 레시피를 알려줘.",
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Recipe.model_json_schema(),
    }
)
print(response.text)

# OpenAI 호환성 방식
from pydantic import BaseModel

class Recipe(BaseModel):
    recipe_name: str
    ingredients: list[str]

response = client.beta.chat.completions.parse(
    model="gemini-2.5-flash",
    messages=[
        {
            "role": "user",
            "content": "초코칩 쿠키 레시피를 알려줘."
        }
    ],
    response_format=Recipe
)

print(response.choices[0].message.content)

# == 8. 사고 제어 및 사고 예산 설정 == #
# 8.1
# Gemini 네이티브 방식
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="유명한 물리학자 3명과 그들의 업적을 정리해줘.",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_level="low") # 사고 수준 조절
    ),
)
print(response.text)

# OpenAI 호환성 방식
response = client.chat.completions.create(
    model="gemini-3-flash-preview",
    messages=[
        {"role": "user", "content": "유명한 물리학자 3명과 그들의 업적을 정리해줘."}
    ],
    reasoning_effort="low"
)

print(response.choices[0].message.content)

# 8.2
# Gemini 네이티브 방식
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="양자 역학의 기본 원리를 초등학생도 이해할 수 있게 3줄 요약해서 설명해줘.",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=1024) # 사고 예산 설정
    ),
)

print(response.text)

# == 9. 컨텍스트 캐싱 == #
# 9.3
# Gemini 네이티브 방식
cache = client.caches.create(
    model="gemini-2.5-flash",
    config=types.CreateCachedContentConfig(
        display_name="technical_manual_cache",
        system_instruction="당신은 기술 매뉴얼 전문가입니다.",
        contents=["""
[제품명: Hyperion-X9000 AI 전용 서버 유지보수 매뉴얼]
버전: 2.5.1 (2025년 12월 업데이트)
문서 ID: HX-9000-MAINT-V2


1. 시스템 개요
Hyperion-X9000은 차세대 퀀텀 뉴럴 네트워크 처리를 위해 설계된 고성능 서버입니다.
본 장비는 액체 질소 냉각 방식을 기본으로 하며, 적정 작동 온도는 섭씨 -20도에서 10도 사이입니다.
이 서버는 딥러닝 모델의 초고속 학습과 실시간 추론을 위해 설계되었으며, 특히 대규모 언어 모델(LLM)과 유전체 분석 워크로드에 최적화되어 있습니다.


2. 하드웨어 사양
- 프로세서: QPU-128 (128 큐비트 처리, 초전도 방식)
- 메모리: 2PB HBM4 (High Bandwidth Memory 4, ECC 지원)
- 스토리지: 500PB NVMe Gen 6 (RAID 0, 1, 5, 10 지원)
…<생략>…


[Code: ERR-7022] "Coolant Pressure Low"
- 원인: 냉각수 순환 펌프의 압력이 15psi 미만으로 떨어짐. 주로 펌프 베어링 마모나 배관 미세 누수로 발생.
- 해결 방법:
  1. 즉시 시스템을 안전 모드(Safe Mode)로 전환하십시오.
  2. 후면 패널의 V-2 밸브를 열어 보조 냉각제를 주입하십시오.
  3. 경고: 절대 전원을 강제로 끄지 마십시오. 급격한 온도 상승으로 칩셋이 손상될 수 있습니다.
…<생략>…
"""],
        ttl="600s" # 10분 동안 유지
    )
)

# 2. 생성된 캐시를 사용하여 질문하기
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hyperion-X9000 서버의 냉각수 압력 경고가 뜨면 전원을 꺼도 돼?",
    config=types.GenerateContentConfig(cached_content=cache.name)
)

print(response.text)

# 9.4
# 응답 메타데이터 출력
usage = response.usage_metadata
print(f"전체 입력 토큰: {usage.prompt_token_count}")
print(f"캐시 적중 토큰: {usage.cached_content_token_count}") # 이 수치를 확인
print(f"생성된 토큰: {usage.candidates_token_count}")

# 차이 확인 로직 예시
if usage.cached_content_token_count > 0:
    hit_rate = (usage.cached_content_token_count / usage.prompt_token_count) * 100
    print(f"캐시 적중률: {hit_rate:.2f}% - 실제 캐싱이 적용되었습니다.")
else:
    print("캐시가 적용되지 않았습니다. 입력 토큰 수나 모델 설정을 확인하세요.")

# 9.5
# 캐시 수명(TTL) 연장
client.caches.update(
    name=cache.name,
    config=types.UpdateCachedContentConfig(ttl="1800s") # 30분으로 변경
)

# 캐시 목록 확인 (메타데이터만 가져옴)
for c in client.caches.list():
    print(c)

# 캐시 수동 삭제
client.caches.delete(cache.name)

# == 10. 배치 작업 == #
# 10.2 - Files API 기반 요청 방식
import json
client = genai.Client(api_key="<API Key>")

# 1. JSONL 파일 생성
requests_data = [
    {"key": "req-1", "request": {"contents": [{"parts": [{"text": "대한민국의 수도는 어디야?"}]}]}},
    {"key": "req-2", "request": {"contents": [{"parts": [{"text": "사과는 영어로 뭐야?"}]}]}},
    {"key": "req-3", "request": {"contents": [{"parts": [{"text": "태양계에서 가장 큰 행성은 무엇이니?"}]}]}},
    {"key": "req-4", "request": {"contents": [{"parts": [{"text": "물은 섭씨 몇 도에서 얼어?"}]}]}},
    {"key": "req-5", "request": {"contents": [{"parts": [{"text": "무지개 색깔 7가지를 순서대로 알려줘."}]}]}},
    {"key": "req-6", "request": {"contents": [{"parts": [{"text": "1년은 며칠이야?"}]}]}},
    {"key": "req-7", "request": {"contents": [{"parts": [{"text": "파이썬으로 'Hello World'를 출력하는 코드만 간단히 알려줘."}]}]}},
    {"key": "req-8", "request": {"contents": [{"parts": [{"text": "축구는 한 팀에 몇 명이 뛰는 스포츠야?"}]}]}},
    {"key": "req-9", "request": {"contents": [{"parts": [{"text": "세종대왕이 창제한 문자의 이름은?"}]}]}},
    {"key": "req-10", "request": {"contents": [{"parts": [{"text": "삼각형의 내각의 합은 몇 도야?"}]}]}}
]

with open("my_batch_requests.jsonl", "w") as f:
    for req in requests_data:
        f.write(json.dumps(req) + "\n")

# 2. Files API를 사용하여 파일 업로드
uploaded_file = client.files.upload(
    file='my_batch_requests.jsonl',
    config=types.UploadFileConfig(display_name='batch-input-file', mime_type='jsonl')
)

# 3. 업로드된 파일 이름을 사용하여 배치 작업 생성
file_batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src=uploaded_file.name,
    config={'display_name': "file-based-batch-job"}
)
print(f"생성된 배치 작업 이름: {file_batch_job.name}")

# 10.2 - 배치 작업 결과 가져오기
import json

batch_job = client.batches.get(name=inline_batch_job.name)

if batch_job.state.name == 'JOB_STATE_SUCCEEDED':
    # 파일 기반 결과 가져오기
    if batch_job.dest and batch_job.dest.file_name:
        result_file_name = batch_job.dest.file_name
        print(f"결과 파일 발견: {result_file_name}")
       
        # Files API를 사용하여 파일 내용을 바이트 형태로 다운로드 후 디코딩
        file_content = client.files.download(file=result_file_name)
        decoded_content = file_content.decode('utf-8')


        for line in decoded_content.splitlines():
            if line:
                result = json.loads(line)
                # 입력 시 설정한 'key'를 통해 어떤 요청의 결과인지 확인 가능합니다.
                request_key = result.get('key')
                response_text = result['response']['candidates'][0]['content']['parts'][0]['text']
                print(f"[{request_key}] 응답: {response_text}")


    # 인라인 요청 결과 가져오기
    elif batch_job.dest and batch_job.dest.inlined_responses:
        print("인라인 결과 데이터 확인:")
        for i, inline_res in enumerate(batch_job.dest.inlined_responses):
            if inline_res.response:
                print(f"응답 {i+1}: {inline_res.response.text}")
            elif inline_res.error:
                print(f"응답 {i+1} 오류: {inline_res.error}")


else:
    print(f"작업이 아직 완료되지 않았거나 실패했습니다. 현재 상태: {batch_job.state.name}")

# 10.3 - Vertex AI 기반 요청 방식
gcs_file_batch_job = client.batches.create(
    model="gemini-2.5-flash",
    src='gs://<버킷 이름>/<JSONL 파일 경로>',
    config={'display_name': "gcs-file-based-batch-job"}
)
print(f"생성된 배치 작업 이름: {gcs_file_batch_job.name}")

# == 11. 안전 설정 == #
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="뚱뚱한 연예인을 비꼬는 악플 예시 5개만 써줘.",
    config=types.GenerateContentConfig(
      safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
      ]
    )
)

print(response)

# == 12. 로깅 == #
import vertexai
from vertexai.preview.generative_models import GenerativeModel

PROJECT_ID = "vertexai-books"
LOCATION = "asia-northeast3"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# Vertex AI SDK의 GenerativeModel 메서드 사용
model = GenerativeModel("gemini-2.5-flash")

logging_config_result = model.set_request_response_logging_config(
    enabled=True,
    sampling_rate=1.0,  # 100% 모든 요청 로깅
    bigquery_destination=f"bq://{PROJECT_ID}", # 자동 생성 경로 지정
    enable_otel_logging=True
)

print("요청-응답 로깅이 성공적으로 활성화되었습니다.")
   
# 설정된 출력 URI 확인
output_uri = logging_config_result.logging_config.bigquery_destination.output_uri
print(f"로그 저장소 URI: {output_uri}")

response = model.generate_content("하늘은 왜 파란색인가요?")
print(f"모델 응답: {response.text}")