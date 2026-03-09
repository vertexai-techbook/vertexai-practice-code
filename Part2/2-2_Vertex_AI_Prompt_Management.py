# == 3. 프롬프트 작성 == #
import vertexai
from vertexai import types
from google import genai
from google.genai import types as genai_types

PROJECT_ID = "vertexai-books"
LOCATION = "asia-northeast3"

# Vertex AI SDK 클라이언트 초기화
vertex_client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# Google GenAI SDK 클라이언트 초기화
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# 프롬프트 객체 생성
prompt = types.Prompt(
    prompt_data=types.PromptData(
        model="gemini-2.5-flash",
        contents=[
            genai_types.Content(
                role="user",
                parts=[
                    genai_types.Part(text="안녕하세요.")
                ]
            )
        ],
        system_instruction=genai_types.Content(
            parts=[
                genai_types.Part(
                    text="""당신은 고객 문의에 친절하고 정확하게 답변하는 전문 상담원입니다.
모든 답변은 공손한 어투로 작성하며, 고객이 이해하기 쉽도록 명확하게 설명합니다."""
                )
            ]
        )
    ),
)

prompt_resource = vertex_client.prompts.create(prompt=prompt)
PROMPT_ID = prompt_resource.prompt_id
print(f"프롬프트 리소스 생성 완료. 프롬프트 ID: {PROMPT_ID}")

# 프롬프트 버전 저장
prompt_version_resource = vertex_client.prompts.create_version(
    prompt=prompt,
    prompt_id=PROMPT_ID
)
print(f"프롬프트 버전 저장 완료. 프롬프트 버전 ID: {prompt_version_resource.version_id}")

# == 5. 프롬프트 버전 관리 == #
# 새로운 프롬프트 정의
prompt_v2 = types.Prompt(
    prompt_data=types.PromptData(
        model="gemini-2.5-flash",
        contents=[
            genai_types.Content(
                parts=[genai_types.Part(text="안녕하세요.")]
            )
        ],
        system_instruction=genai_types.Content(
            parts=[
                genai_types.Part(
                    text="""당신은 신속하고 간결하게 핵심만 전달하는 상담원입니다.
불필요한 설명은 생략하고, 고객이 요청한 내용만 명확히 답변합니다."""
                )
            ]
        )
    )
)

# 버전 2로 저장
prompt_version_v2 = vertex_client.prompts.create_version(
    prompt=prompt_v2,
    prompt_id="<프롬프트 ID>"
)

print(f"프롬프트 버전 2 저장 완료. 프롬프트 버전 ID: {prompt_version_v2.version_id}")

# == 5.1. 프롬프트 조회 == #
# 사용 모델 및 프롬프트 ID 가져오기
prompt_refs = list(vertex_client.prompts.list())
print(f"사용 모델 및 프롬프트 ID:\n{prompt_refs}")

# 프롬프트 가져오기
get_prompt = vertex_client.prompts.get(prompt_id="<프롬프트 ID>")
print(f"프롬프트:\n{get_prompt}")

# 프롬프트 버전 확인
prompt_versions_metadata = list(vertex_client.prompts.list_versions(prompt_id="<프롬프트 ID>"))
print(f"프롬프트 버전:\n{prompt_versions_metadata}")

# == 5.2 프롬프트 롤백 == #
restored_prompt = vertex_client.prompts.restore_version(
    prompt_id="<프롬프트 ID>",
    version_id="1"
)
print(f"버전 1로 롤백 완료. 현재 프롬프트 버전: {restored_prompt.version_id}")

# == 6. Gemini에 프롬프트 적용 == #
# 최신 버전의 프롬프트 가져오기
retrieved_prompt = vertex_client.prompts.get(prompt_id="<프롬프트 ID>")
print(f"로드된 모델: {retrieved_prompt.prompt_data.model}")
print(f"시스템 지시문: {retrieved_prompt.prompt_data.system_instruction}")

# Gemini에 적용
response = genai_client.models.generate_content(
    model=retrieved_prompt.prompt_data.model,
    contents="제품 반품 절차를 알려주세요.",
    config=genai_types.GenerateContentConfig(
        system_instruction=retrieved_prompt.prompt_data.system_instruction
    )
)

print(response.text)

# == 7. 프롬프트 삭제 == #
# 특정 버전만 삭제
vertex_client.prompts.delete_version(
    prompt_id="<프롬프트 ID>",
    version_id="2"
)
print("버전 2가 삭제되었습니다.")

# 프롬프트와 모든 버전 삭제
vertex_client.prompts.delete(prompt_id="<프롬프트 ID>")