import os
import uvicorn
import asyncio
from typing import TypedDict, Annotated, Sequence, Any, Literal

# A2A 및 LangChain/LangGraph 관련 라이브러리
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCard, AgentCapabilities, AgentSkill, TaskState, Part, TextPart
from a2a.utils import new_agent_text_message, new_task

from langchain_core.messages import BaseMessage, AIMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_mcp_adapters.client import MultiServerMCPClient

GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

# Step 1: LangGraph 로직 정의 - 에이전트 설계
# LangGraph의 대화 흐름(상태)을 관리하는 객체 정의
# messages: 사용자와 에이전트가 주고받는 대화 기록
def add_messages(previous_conversation: list, conversation: list) -> list:
    """대화 기록을 누적하기 위한 간단한 함수"""
    return previous_conversation + conversation

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# LangGraph 기반의 AI 에이전트 앱을 생성하는 함수
def create_langgraph_app(tools: list):
    """LangGraph 워크플로우를 생성하고 컴파일합니다."""
   
    # 1-1. LLM 모델 설정
    model = ChatVertexAI(model_name="gemini-2.5-flash", temperature=0)

    # LLM이 MCP 서버에서 가져온 Tool을 사용할 수 있도록 연결
    model_with_tools = model.bind_tools(tools)
   
    # 1-2. LLM에게 역할을 부여하는 시스템 프롬프트 정의
    system_prompt = (
        "당신은 실시간 날씨 정보를 제공하는 친절한 어시스턴트입니다."
        "1. 먼저 ‘get_geocoding’ 도구를 사용하여 해당 도시의 위도와 경도를 찾으세요."
        "2. 그 다음, ‘get_weather_data’ 도구를 사용하여 날씨 정보를 조회하세요."
        "조회된 정보를 바탕으로 친절하고 이해하기 쉬운 한국어로 답변해 주세요."
    )

    # 1-3. Graph의 각 노드(Node)에서 수행할 함수 정의
    # call_model: LLM을 호출하여 다음 행동을 결정하거나 최종 답변을 생성
    def call_model(state: AgentState):
        # 대화 기록 맨 앞에 시스템 프롬프트를 추가하여 LLM의 역할을 명확히 함
        messages_with_system_prompt = [SystemMessage(content=system_prompt)] + state["messages"]
        response = model_with_tools.invoke(messages_with_system_prompt)
        return {"messages": [response]}
       
    # should_continue: LLM의 답변에 따라 Tool을 호출할지, 대화를 종료할지 결정
    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        last_message = state["messages"][-1]

        # LLM이 Tool을 호출해야 한다고 판단했다면 'tools' 노드로 이동
        if last_message.tool_calls:
            return "tools"
           
        # 그렇지 않으면 대화 종료
        return "__end__"

    # 1-4. Graph 워크플로우 구성
    workflow = StateGraph(AgentState)
    tool_node = ToolNode(tools) # Tool을 실행하는 노드
   
    workflow.add_node("agent", call_model) # 'agent' 노드 추가
    workflow.add_node("tools", tool_node) # 'tools' 노드 추가
   
    workflow.set_entry_point("agent") # 'agent' 노드에서 작업 시작
   
    # 'agent' 노드의 결과에 따라 다음 경로를 동적으로 결정
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )
    # 'tools' 노드 작업이 끝나면 다시 'agent' 노드로 돌아가 최종 답변 생성
    workflow.add_edge("tools", "agent")
   
    return workflow.compile()

# Step 2: A2A 프로토콜과 LangGraph 연결 - 통신 채널 구축
# A2A 서버의 요청을 받아 LangGraph 에이전트를 실행시키는 클래스
class LangGraphA2AExecutor(AgentExecutor):
    def __init__(self, graph: Any):
        self.graph = graph
        self._cancelled_task_ids: set[str] = set() # 작업 취소 요청을 추적

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
       
        # A2A 프로토콜의 작업(Task) 상태를 관리하는 객체
        task = context.current_task or new_task(context.message)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.start_work() # 클라이언트에게 "작업 시작됨"을 알림

        config = {"configurable": {"thread_id": task.id}}
        graph_input = {"messages": [("human", user_query)]}
       
        final_result_chunk = None
        accumulated_text = ""

        # LangGraph 에이전트를 스트리밍 방식으로 실행
        async for chunk in self.graph.astream(graph_input, config=config):
            if task.id in self._cancelled_task_ids:
                print(f"작업 취소됨: {task.id}")
                break

            final_result_chunk = chunk
            partial_text = self._extract_text_from_chunk(chunk)
           
            # 이전과 다른 새로운 텍스트 조각이 생성되면 클라이언트에게 실시간 전송
            if partial_text and partial_text != accumulated_text:
                new_delta = partial_text[len(accumulated_text):]
                await updater.update_status(
                    TaskState.working,
                    message=new_agent_text_message(new_delta, task.context_id, task.id)
                )
                accumulated_text = partial_text

        # 최종 결과물을 A2A 'Artifact' 형태로 클라이언트에게 전송
        final_text = self._extract_text_from_chunk(final_result_chunk)
        await updater.add_artifact([Part(root=TextPart(text=final_text))])
        await updater.complete() # 클라이언트에게 "작업 완료됨"을 알림

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """A2A 작업 취소 요청을 처리합니다."""
        task = context.current_task
        if task:
            self._cancelled_task_ids.add(task.id)
            updater = TaskUpdater(event_queue, task.id, task.context_id)
            await updater.cancel(message=new_agent_text_message("작업이 취소되었습니다."))

# Step 3: 서버 실행 - 에이전트를 외부에 노출
async def main():
    """MCP 클라이언트 설정, A2A 서버 구성 및 실행을 담당합니다."""

    # 3-1. MCP 클라이언트 설정
    mcp_server_url = "http://localhost:7000/mcp/"
    mcp_client = MultiServerMCPClient({
        "weather_server": {"transport": "streamable_http", "url": mcp_server_url}
    })
    # MCP 서버에 연결하여 Tool 목록을 가져옴
    weather_tools = await mcp_client.get_tools()
    print(f"✅ MCP 서버에서 {len(weather_tools)}개의 Tool을 로드했습니다.")

    # 3-2. LangGraph 앱 생성 (Step 1에서 정의)
    graph_app = create_langgraph_app(tools=weather_tools)

    # 3-3. AgentCard 정의
    agent_card = AgentCard(
        name="LangGraph Weather Agent",
        description="LangGraph와 MCP Tool을 연동한 실시간 날씨 정보 제공 에이전트",
        url="http://localhost:8000",
        version="2.0.0",
        skills=[
            AgentSkill(
                id="weather-qa-skill",
                name="Real-time Weather Q&A",
                description="MCP Tool을 사용하여 특정 지역의 실시간 날씨 정보를 제공합니다.",
                tags=["weather", "langgraph", "mcp"],
                examples=["서울 날씨 어때?", "부산의 현재 온도를 알려줘"],
            )
        ],
        capabilities=AgentCapabilities(streaming=True),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )

    # 3-5. A2A 서버 구성 (Step 2에서 정의한 Executor 사용)
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

    # 3-6. Uvicorn을 사용하여 A2A 서버 실행
    print(f"🚀 LangGraph A2A 에이전트 서버를 시작합니다.")
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())