import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

# 클라이언트 초기화
client = genai.Client(vertexai=True, project="vertexai-books", location="global")

# MCP 서버 실행 파라미터 정의: stdio 방식으로 로컬 Filesystem 서버를 실행
server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem",
          "/home/ubuntu/VertexAI-Books/Part4"],  # 본인 경로로 변경
    env=None,
)

async def run():
    # stdio 전송 방식으로 MCP 서버에 연결
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 클라이언트-서버 간 초기화 (핸드셰이크)
            await session.initialize()


            # 연결된 MCP 서버가 제공하는 도구 목록 확인
            tools = await session.list_tools()
            print("## 사용 가능한 MCP 도구 목록")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")


            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents="현재 디렉토리의 파일 목록 보여주고, Function_Calling 폴더에 있는 python 파일들에 대해서 요약해줘.",
                config=types.GenerateContentConfig(
                    temperature=0,
                    tools=[session],  # MCP 세션을 도구로 전달
                ),
            )
            print("\n## 모델 응답")
            print(response.text)

# 비동기 실행
asyncio.run(run())