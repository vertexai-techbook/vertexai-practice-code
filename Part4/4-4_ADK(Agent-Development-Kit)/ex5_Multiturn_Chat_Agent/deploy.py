import os
from dotenv import load_dotenv
import vertexai
from agent import chatbot_agent
from vertexai import agent_engines

# 환경 변수 로드
load_dotenv()

# 환경 변수 가져오기
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# 1단계: Agent Engine 초기화
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=BUCKET_NAME
)

# 2단계: 에이전트를 AdkApp 객체로 래핑
app = agent_engines.AdkApp(
    agent=chatbot_agent,
    enable_tracing=True,
)

# 3단계: Agent Engine에 배포
# Agent Engine이 환경을 구축할 때 필요한 라이브러리를 지정합니다.
remote_app = agent_engines.create(
    agent_engine=app,
    requirements=["google-cloud-aiplatform[agent_engines]", "google-adk", "cloudpickle==3.0", "python-dotenv"],
    gcs_dir_name='Chatbot/agent_engine',
    display_name='adk_multiturn_agent',
    description='ADK기반 Multi-turn 챗봇 에이전트입니다.',
    extra_packages=["agent.py"],
)

# 배포된 에이전트의 고유 식별자: projects/.../reasoningEngines/{RESOURCE_ID}
print(f"리소스 이름 (Resource Name): {remote_app.resource_name}")
