import asyncio

from google import genai
from google.genai.types import Content, FunctionDeclaration, GenerateContentConfig, Part, Tool
from toolbox_core import ToolboxClient

prompt = """
당신은 온라인 전자상거래 플랫폼의 데이터 분석 전문가 입니다.
사용자의 질문에서 적절한 값들을 추출하여 알맞은 도구를 호출해야 합니다.

1. 사용자가 특정 도시의 고객 목록을 물어보면 질문에서 도시 이름을 추출하여 'get_customers_by_city' 도구를 호출합니다.
2. 사용자가 특정 카테고리의 총 판매 수량과 총 매출을 알고싶어 한다면 질문에서 카테고리를 추출하여 'get_sales_by_category' 도구를 호출합니다.
3. 혹은 특정 기간 동안의 일별 총 주문 건수를 조회하고자 한다면 시작 날짜와 끝 날짜를 추출하여 'get_daily_order_count' 도구를 호출합니다.
4. 가장 많이 구매한 상위 n명의 VIP 고객이 누군지 알고싶어 한다면 몇 명을 궁금해하는지 추출하여 'get_top_customers'도구를 호출합니다.
"""

queries = [
    "가장 많이 구매한 상위 10명이 누구야?",
    "부산 사는 고객들 정보 알려줘.",
    "23년 1월부터 2월까지 얼마나 팔렸어?",
    "전자제품의 총 판매 수량 좀 알려줘.",
]

async def run_application():
    # Toolbox 서버에 연결하고 툴셋 로드
    async with ToolboxClient("http://127.0.0.1:5000") as toolbox_client:
        toolbox_tools = await toolbox_client.load_toolset("ecommerce_toolset")

        # 도구 이름을 key로 하는 딕셔너리 생성
        tool_map = {tool._name: tool for tool in toolbox_tools}
        genai_client = genai.Client(
            vertexai=True, project="vertexai-books", location="asia-northeast3"
        )

        genai_tools = [
            Tool(
                function_declarations=[
                    FunctionDeclaration.from_callable_with_api_option(callable=tool)
                ]
            )
            for tool in toolbox_tools
        ]
        history = []
        for query in queries:
            print(f"\n--- 질문 {query} ---\n")
            user_prompt_content = Content(
                role="user",
                parts=[Part.from_text(text=query)],
            )
            history.append(user_prompt_content)

            response = genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=history,
                config=GenerateContentConfig(
                    system_instruction=prompt,
                    tools=genai_tools,
                ),
            )
            history.append(response.candidates[0].content)
            function_response_parts = []
           
            for function_call in response.function_calls:
                fn_name = function_call.name

                # 딕셔너리를 사용하여 이름으로 도구를 안전하게 찾고 호출
                if fn_name in tool_map:
                    selected_tool = tool_map[fn_name]
                    print(f"호출 도구: {fn_name} 매개변수: {function_call.args}")
                    function_result = await selected_tool(**function_call.args)
                else:
                    print(f"Error: Function name '{fn_name}' not found in the toolset.")
                    function_result = f"'{fn_name}' 도구가 존재하지 않습니다."
               
                function_response = {"result": function_result}
                function_response_part = Part.from_function_response(
                    name=function_call.name,
                    response=function_response,
                )
                function_response_parts.append(function_response_part)

            if function_response_parts:
                tool_response_content = Content(role="tool", parts=function_response_parts)
                history.append(tool_response_content)

                response2 = genai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=history,
                    config=GenerateContentConfig(
                        tools=genai_tools,
                    ),
                )
                final_model_response_content = response2.candidates[0].content
                history.append(final_model_response_content)
                print(f"\n답변:\n{response2.text}\n")
            else:
                # 도구를 사용하지 않고 바로 답변한 경우
                print(f"\n답변(No Tool Used):\n{response.text}\n")

asyncio.run(run_application())