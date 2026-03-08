import asyncio
import os
from dotenv import load_dotenv


from google.adk.agents import LlmAgent, Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.runners import Runner
from google.adk.sessions import VertexAiSessionService
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools import google_search
from google.genai import types

# 환경 변수 로드
load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID") # 위에서 복사한 ENGINE_ID

# Vertex AI Agent Engine 기반 세션 & 메모리 설정
session_service_instance = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION
)
memory_service_instance = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location=LOCATION,
    agent_engine_id=AGENT_ENGINE_ID
)

# 1. 검색 전문 에이전트
search_agent  = LlmAgent(
    name="SearchAgent",
    model="gemini-2.5-flash",
    instruction="당신은 웹 검색 전문가입니다. 사용자 질문에 대한 최신 정보를 Google 검색 도구를 사용하여 답변하세요.",
    description="Google 검색을 통해 정보를 찾는 검색 에이전트입니다.",
    tools=[google_search],
)

# 2. 오케스트레이션 에이전트 (에이전트를 도구로 사용 Agent-as-a-Tool)
chatbot_agent = LlmAgent(
    name="ConversationAgent",
    model="gemini-2.5-flash",
    instruction="""
    당신은 사용자와 다중 턴 대화를 나누며 정보를 기억하고 활용하는 친근한 챗봇입니다.
    이전 대화 내용을 기억하여 사용자의 질문에 맥락에 맞게 답변하세요.
   
    단순한 질문의 경우 사용자 질문에 직접 응대하고, 최신 정보가 필요한 질문의 경우 'SearchAgent' 도구를 사용하여 검색하세요.
    과거의 대화나 학습된 정보를 활용하여 답변에 참고하세요.
    """,
    description="대화형 챗봇 에이전트입니다.",
    tools=[AgentTool(agent=search_agent)]
)

# Runner 설정 및 실행 함수
async def main():
    user_id = "user_123"

    # 세션 생성 (VertexAISessionService는 session_id를 자동으로 생성하고 반환합니다.)
    session = await session_service_instance.create_session(
        app_name=AGENT_ENGINE_ID,
        user_id=user_id
    )

    runner = Runner(
        agent=chatbot_agent,
        app_name=AGENT_ENGINE_ID,
        session_service=session_service_instance,
        memory_service=memory_service_instance,
    )

    print(f"챗봇이 시작되었습니다. (세션 ID: {session.id}, 사용자 ID: {user_id})")
    print("대화를 종료하려면 'exit'을 입력하세요.")

    while True:
        user_query = input("\n사용자👨‍💻 > ")
        if user_query.lower() == 'exit':
            print("챗봇을 종료합니다. 안녕히 가세요!")
            break

        content = types.Content(role='user', parts=[types.Part(text=user_query)])

        final_text_responses = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=content
        ):
            if event.is_final_response() and event.content.parts:
                final_text_responses = event.content.parts[0].text
                print(f"챗봇✨ > {final_text_responses}")            
       
        # 각 턴이 끝날 때, 업데이트된 세션 내용을 MemoryService에 추가하여 기억 생성
        updated_session = await session_service_instance.get_session(
            app_name=AGENT_ENGINE_ID,
            user_id=user_id,
            session_id=session.id
        )
        if updated_session:
            await memory_service_instance.add_session_to_memory(updated_session)

if __name__ == "__main__":
    asyncio.run(main())