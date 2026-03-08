from google.adk.agents import Agent, LlmAgent, SequentialAgent, LoopAgent
from google.adk.tools.tool_context import ToolContext

# 세션 상태(State) 키 정의
# State는 현재 대화 스레드에만 관련된 임시 데이터를 저장하며, 에이전트 간 데이터 공유에 필수적입니다.
STATE_INITIAL_REQUEST = "initial_code_request"
STATE_CURRENT_CODE = "current_python_code"
STATE_REVIEW_COMMENTS = "review_comments"

# LoopAgent의 반복을 종료시키는 도구 (ToolContext 활용)
def exit_loop(tool_context: ToolContext) -> dict:
    """코드 리뷰에서 더 이상 개선할 필요가 없다고 판단할 때 이 함수를 호출하여 반복 프로세스를 종료합니다."""

    tool_context.actions.escalate = True 
    return {"status": "loop_exited"}

# 1. 초기 Python 코드 작성 에이전트
initial_code_writer_agent = LlmAgent(
    name="InitialCodeWriterAgent",
    model="gemini-2.5-flash",
    include_contents='none', # 이전 대화 기록을 LLM에 보내지 않도록 설정합니다.
    instruction="""당신은 요청에 따라 Python 코드를 작성하는 AI 개발자입니다.
    제공된 요청에 따라 Python 코드를 작성하세요. 오직 완전한 Python 코드 블록만 출력하세요.(```python ... ```로 둘러싸야 합니다.)
    요청: {(initial_code_request)}
    """,
    description="사용자 요청에 따라 초기 Python 코드를 작성합니다.",
    output_key=STATE_CURRENT_CODE 
)

# 2. 코드 리뷰 에이전트: 비전공자도 이해할 수 있는 직관적인 코드인지 검토
code_reviewer_agent = LlmAgent(
    name="CodeReviewerAgent",
    model="gemini-2.5-flash",
    include_contents='none',
    instruction="""당신은 Python 코드 가독성 전문가입니다. 제공된 코드를 '비전공자도 이해할 수 있는 직관적인 코드'인지 검토하세요.
    **검토할 코드:**
    ```python
    {(current_python_code)}
    ```
    **작업:**
    코드를 검토하고 다음 기준에 따라 피드백을 제공하세요:
    1. **문법 난이도:** 복잡한 문법(리스트 컴프리헨션 중첩, 삼항 연산자 체이닝, 데코레이터 남용 등)을 사용하고 있지는 않은가? 초보자도 읽을 수 있는 기본 문법(for문, if문 등)으로 대체할 수 있는가?
    2. **변수/함수 네이밍:** 변수명과 함수명만 보고도 역할을 직관적으로 이해할 수 있는가? 약어나 모호한 이름을 사용하고 있지는 않은가?
    3. **코드 흐름:** 코드를 위에서 아래로 읽었을 때 논리적 흐름이 자연스러운가? 불필요하게 복잡한 구조는 없는가?
    4. **주석 및 설명:** 핵심 로직에 대한 한글 주석이 충분한가? 주석 없이도 이해하기 어려운 부분이 있는가?

    만약 개선할 부분이 있다면 위 기준에 따라 구체적인 지적과 함께 더 쉬운 대안을 제시하고 오직 비평 텍스트만 출력하세요.
    그렇지 않고 코드가 비전공자도 충분히 이해할 수 있을 만큼 직관적이고, 더 이상 단순화할 필요가 없다고 판단된다면 정확히 다음 문구만 출력하세요: '이 코드는 완벽합니다!'
    """,
    description="현재 Python 코드를 비전공자 관점에서 검토하고 직관성 및 가독성에 대한 피드백을 제공합니다.",
    output_key=STATE_REVIEW_COMMENTS
)

# 3. 코드 정제 에이전트: 비평을 반영하여 더 쉽고 직관적인 코드로 개선
code_refiner_agent = LlmAgent(
    name="CodeRefinerAgent",
    model="gemini-2.5-flash",
    include_contents='none',
    instruction="""
    당신은 제공된 코드와 비평을 바탕으로 코드를 더 쉽고 직관적으로 개선하는 Python 개발자입니다.
    **현재 코드:**
    ```python
    {(current_python_code)}
    ```
    **비평/제안:**
    {(review_comments)}

    **작업:**
    '비평/제안'을 분석하세요.
    만약 비평이 정확히 "이 코드는 완벽합니다!"라면 반드시 `exit_loop` 함수를 호출해야 합니다.
    그렇지 않다면 제안을 반영하여 비전공자도 읽기 쉬운 코드로 개선하세요.
    복잡한 문법은 기본 문법으로 풀어쓰고, 변수명은 직관적으로 바꾸며, 핵심 로직에는 한글 주석을 추가하세요.
    오직 개선된 Python 코드 텍스트만 출력하세요. (```python ... ```로 둘러싸야 합니다.)
    개선된 코드만 출력하거나 `exit_loop` 함수를 호출하세요.
    """,
    description="비평에 따라 Python 코드를 비전공자도 이해할 수 있도록 단순화하거나, 비평이 완료 신호를 보내면 루프를 종료합니다.",
    tools=[exit_loop], # 루프 종료 도구 제공
    output_key=STATE_CURRENT_CODE # 개선된 코드를 'current_python_code'에 덮어씀
)

# 루프 에이전트(LoopAgent): 비평과 개선을 반복
code_improvement_loop = LoopAgent(
    name="CodeImprovementLoop",
    sub_agents=[
        code_reviewer_agent, 
        code_refiner_agent,  
    ],
    max_iterations=5, # 무한 루프를 방지하기 위한 최대 반복 횟수 제한.
    description="코드 리뷰 및 개선 작업을 반복적으로 수행합니다."
)

# 순차 에이전트(SequentialAgent): 전체 순차 파이프라인
root_agent = SequentialAgent(
    name="codeOptimizationPipeline",
    sub_agents=[
        initial_code_writer_agent, # 1. 초기 코드 작성 에이전트 실행
        code_improvement_loop,     # 2. 코드 개선 루프 실행
    ],
    description="초기 Python 코드를 작성하고 코드 개선 루프를 통해 반복적으로 최적화합니다.",
)