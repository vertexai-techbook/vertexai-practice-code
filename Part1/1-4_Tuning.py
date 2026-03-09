# == 2. 지도 기반 미세 조정 == #
# 2.1
import time
from google import genai
from google.genai.types import HttpOptions, CreateTuningJobConfig, TuningDataset

# 클라이언트 초기화 (API 버전 v1beta1 사용)
client = genai.Client(vertexai=True, project="vertexai-books", location="us-central1", http_options=HttpOptions(api_version="v1beta1"))

# 학습 및 검증 데이터 세트 설정
training_dataset = TuningDataset(
    gcs_uri="gs://mhkim-data-bucket/Tuning/SFT/training_dataset.jsonl",
)
validation_dataset = TuningDataset(
    gcs_uri="gs://mhkim-data-bucket/Tuning/SFT/validation_dataset.jsonl",
)

# SFT 튜닝 작업 생성
tuning_job = client.tunings.tune(
    base_model="gemini-2.0-flash-001",
    training_dataset=training_dataset,
    config=CreateTuningJobConfig(
        tuned_model_display_name="Gemini_SFT_Expert_Model",
        validation_dataset=validation_dataset,
        # 하이퍼파라미터는 필요시 설정 (기본값 권장)
    ),
)

# 작업 상태 모니터링
while tuning_job.state in ["JOB_STATE_PENDING", "JOB_STATE_RUNNING"]:
    print(f"현재 상태: {tuning_job.state}")
    tuning_job = client.tunings.get(name=tuning_job.name)
    time.sleep(60)

print(f"튜닝 완료. 모델 이름: {tuning_job.tuned_model.model}")

# 2.2
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project="vertexai-books", location="us-central1")

response = client.models.generate_content(
    model="projects/<프로젝트 넘버>/locations/us-central1/endpoints/<모델 엔드포인트 ID>",
    config=types.GenerateContentConfig(system_instruction="사용자 입력 내용을 요약해줘."),
    contents="에이전틱 AI(Agentic AI)는 단일 에이전트가 자율적으로 목표를 설정하고 복잡한 작업을 수행하는 데 초점을 맞추는 반면, 멀티 에이전트 시스템(Multi-Agent System)은 여러 에이전트가 협력하거나 경쟁하며 공동의 목표를 달성하도록 설계되어, 개념적으로는 에이전틱 AI가 더 넓은 자율적 AI 시스템을 포괄하고 멀티 에이전트 시스템은 그 안에서 협업하는 구조를 지칭하는 경우가 많습니다. 즉, 에이전틱 AI는 '일하는 AI' 자체의 자율성을 강조하고, 멀티 에이전트 시스템은 '여러 AI가 팀처럼 일하는 방식'을 설명합니다."
)
print(response.text)

# == 3. 선호도 조정 == #
# 클라이언트 초기화 (API 버전 v1 사용)
client = genai.Client(vertexai=True, project="vertexai-books", location="us-central1", http_options=HttpOptions(api_version="v1"))

# 학습 및 검증 데이터 세트 설정
training_dataset = TuningDataset(
    gcs_uri="gs://mhkim-data-bucket/Tuning/PT/training_dataset.jsonl",
)
validation_dataset = TuningDataset(
    gcs_uri="gs://mhkim-data-bucket/Tuning/PT/validation_dataset.jsonl",
)

# 선호도 조정 작업 생성
tuning_job = client.tunings.tune(
    base_model="gemini-2.5-flash",
    training_dataset=training_dataset,
    config=CreateTuningJobConfig(
        tuned_model_display_name="Gemini_Preference_Model",
        method="PREFERENCE_TUNING",
        validation_dataset=validation_dataset,
    ),
)

# 작업 상태 모니터링
while tuning_job.state in ["JOB_STATE_PENDING", "JOB_STATE_RUNNING"]:
    print(f"현재 상태: {tuning_job.state}")
    tuning_job = client.tunings.get(name=tuning_job.name)
    time.sleep(60)

print(f"튜닝 완료. 모델 이름: {tuning_job.tuned_model.model}")
