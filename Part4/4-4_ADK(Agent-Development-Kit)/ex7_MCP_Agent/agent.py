import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# ※반드시 절대 경로로 입력해야 합니다※
TARGET_FOLDER_PATH = "<접근 허용할 폴더의 절대 경로>"

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='filesystem_assistant_agent',
    instruction=f"""
    당신은 MCP 기반 파일시스템 에이전트입니다.
    현재 사용자가 제공한 접근 가능한 폴더는 {TARGET_FOLDER_PATH}입니다.
    이 디렉토리 안에 있는 폴더 및 파일들에 관하여 탐색하고, 분석하여 사용자와 상호작용해야 합니다.
    """,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        os.path.abspath(TARGET_FOLDER_PATH),
                    ],
                ),
            ),
            # 내장되어 있는 도구 중 원하는 작업만 하도록 필터링할 수 있습니다.
            # tool_filter=['list_directory', 'read_file']
        )
    ],
)