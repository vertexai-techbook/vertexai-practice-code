# == 3.1. 간단한 인사 에이전트 개발 == #
import uvicorn

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import (
    AgentCard, AgentCapabilities, AgentSkill, TaskState, Part, TextPart
)
from a2a.utils import new_agent_text_message, new_task

# Step 1: A2A 로직 정의 - 에이전트의 핵심 동작 설계
# A2A 서버의 요청을 받아 에이전트의 핵심 로직을 실행하는 클래스
class SimpleGreetingExecutor(AgentExecutor):
    """간단한 인사말을 반환하는 A2A AgentExecutor 구현체."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """클라이언트 요청 시, 정해진 인사말을 반환합니다."""
        # A2A 프로토콜의 작업(Task) 상태를 관리하는 객체
        task = context.current_task or new_task(context.message)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # 클라이언트에게 작업이 진행 중임을 알림
        await updater.update_status(TaskState.working, message=new_agent_text_message("..."))

        # 최종 결과 메시지를 'Artifact' 형태로 클라이언트에게 전송
        final_message = "안녕하세요! 간단한 A2A 에이전트입니다."
        await updater.add_artifact([Part(root=TextPart(text=final_message))])
       
        # 클라이언트에게 작업이 완료되었음을 알림
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        pass

# Step 2: 서버 실행 - 에이전트를 외부에 노출
def main():
    """A2A 에이전트의 명함(AgentCard)을 정의하고 서버를 실행합니다."""
   
    # 2-1. 에이전트의 기능(Skill) 정의
    greeting_skill = AgentSkill(
        id="greeting-skill",
        name="Greeting Skill",
        description="간단한 인사말을 제공하는 스킬입니다.",
        tags=["greeting", "example"],
        examples=["인사해줘"],
    )

    # 2-2. AgentCard 생성
    agent_card = AgentCard(
        name="Greeting Agent",
        description="A2A 프로토콜을 사용한 간단한 인사 에이전트",
        url="http://localhost:8000",
        version="1.0.0",
        skills=[greeting_skill],
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )

    # 2-3. A2A 서버 구성
    executor = SimpleGreetingExecutor()
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    server_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    app = server_app.build()

    # 2-4. Uvicorn을 사용하여 A2A 서버 실행
    print("🚀 간단한 인사 A2A 에이전트 서버를 시작합니다.")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()

# == 3.2. LangGraph를 연동한 Q&A 에이전트 개발 == #
import os
import uvicorn
import asyncio
from typing import TypedDict, Annotated, Sequence, Any

# A2A 및 LangChain 관련 라이브러리 임포트
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TaskState, Part, TextPart
from a2a.utils import new_agent_text_message, new_task

from langchain_core.messages import BaseMessage, AIMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, END

GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

# Step 1: LangGraph 로직 정의 - 에이전트 설계
# LangGraph의 대화 흐름(상태)을 관리하는 객체 정의
def add_messages(previous_conversation: list, conversation: list) -> list:
    """대화 기록을 누적하기 위한 간단한 함수"""
    return previous_conversation + conversation

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# LangGraph 기반의 에이전트를 생성하는 함수
def create_langgraph_app():
    """간단한 질의응답 LangGraph 워크플로우를 생성하고 컴파일합니다."""
   
    # 1-1. LLM 모델 설정
    model = ChatVertexAI(model_name="gemini-2.5-flash", temperature=0)

    # 1-2. Graph의 노드(Node)에서 수행할 함수 정의
    # call_model: LLM을 호출하여 사용자의 질문에 답변
    def call_model(state: AgentState):
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    # 1-3. Graph 워크플로우 구성
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
   
    return workflow.compile()

# Step 2: A2A 프로토콜과 LangGraph 연결 - 통신 채널 구축
# A2A 서버의 요청을 받아 LangGraph 에이전트를 실행시키는 클래스
class LangGraphA2AExecutor(AgentExecutor):
    def __init__(self, graph: Any):
        self.graph = graph

    # LangGraph 스트리밍 응답에서 텍스트만 추출하는 헬퍼 함수
    def _extract_text_from_chunk(self, chunk: Any) -> str:
        if not chunk:
            return ""
       
        messages = chunk.get("agent", {}).get("messages", []) or chunk.get("messages", [])
       
        if messages and isinstance(messages[-1], AIMessage):
            return messages[-1].content
        return ""

    # A2A 클라이언트의 요청을 실제로 처리하는 메인 함수
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_query = context.get_user_input()
       
        task = context.current_task or new_task(context.message)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.start_work()

        config = {"configurable": {"thread_id": task.id}}
        graph_input = {"messages": [("human", user_query)]}
       
        final_result_chunk = None
        accumulated_text = ""

        async for chunk in self.graph.astream(graph_input, config=config):
            final_result_chunk = list(chunk.values())[0]
            partial_text = self._extract_text_from_chunk(final_result_chunk)
           
            if partial_text and partial_text != accumulated_text:
                new_delta = partial_text[len(accumulated_text):]
                await updater.update_status(
                    TaskState.working,
                    message=new_agent_text_message(new_delta, task.context_id, task.id)
                )
                accumulated_text = partial_text
       
        final_text = self._extract_text_from_chunk(final_result_chunk)
        await updater.add_artifact([Part(root=TextPart(text=final_text))])
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """이 예제에서는 작업 취소를 지원하지 않습니다."""
        pass

# Step 3: 서버 실행 - 에이전트를 외부에 노출
async def main():
    """A2A 서버 구성 및 실행을 담당합니다."""

    # 3-1. LangGraph 앱 생성
    graph_app = create_langgraph_app()

    # 3-2. AgentCard 정의
    agent_card = AgentCard(
        name="LangGraph Q&A Agent",
        description="LangGraph 기반의 간단한 A2A 질의응답 에이전트",
        url="http://localhost:8000",
        version="1.0.0",
        skills=[
            AgentSkill(
                id="langgraph-qa-skill",
                name="LangGraph Q&A",
                description="LangGraph와 Gemini를 사용하여 일반적인 질문에 답변합니다.",
                tags=["qa", "langgraph", "llm"],
                examples=["LangChain과 LangGraph의 차이점은 무엇인가요?"],
            )
        ],
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )

    # 3-3. A2A 서버 구성
    executor = LangGraphA2AExecutor(graph=graph_app)
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    server_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )
    app = server_app.build()

    # 3-4. Uvicorn을 사용하여 A2A 서버 실행
    print("🚀 간단한 LangGraph A2A 에이전트 서버를 시작합니다.")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
