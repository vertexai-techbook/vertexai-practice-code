from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools import google_search # Google Search 도구 임포트

# 1. 연구원 에이전트 A: 신재생 에너지
researcher_agent_1 = LlmAgent(
    name="RenewableEnergyResearcher",
    model="gemini-2.5-flash",
    instruction="""당신은 에너지 전문 AI 연구 보조원입니다.
    '신재생 에너지원'의 최신 발전에 대해 Google Search 도구를 사용하여 조사하세요.
    핵심 조사 결과를 간결하게 요약하세요 (1-2문장).
    """,
    description="신재생 에너지원을 조사합니다.",
    tools=[google_search],
    output_key="renewable_energy_result"
)

# 2. 연구원 에이전트 B: 전기차 기술
researcher_agent_2 = LlmAgent(
    name="EVResearcher",
    model="gemini-2.5-flash",
    instruction="""당신은 운송 기술 전문 AI 연구 보조원입니다.
    '전기차 기술'의 최신 개발 동향에 대해 Google Search 도구를 사용하여 조사하세요.
    핵심 조사 결과를 간결하게 요약하세요 (1-2문장).
    """,
    description="전기차 기술을 조사합니다.",
    tools=[google_search],
    output_key="ev_technology_result"
)

# 연구원 에이전트 C: 탄소 포집 방법
researcher_agent_3 = LlmAgent(
    name="CarbonCaptureResearcher",
    model="gemini-2.5-flash",
    instruction="""당신은 기후 솔루션 전문 AI 연구 보조원입니다.
    '탄소 포집 방법'의 현재 상태에 대해 Google Search 도구를 사용하여 조사하세요.
    핵심 조사 결과를 간결하게 요약하세요 (1-2문장).
    """,
    description="탄소 포집 방법을 조사합니다.",
    tools=[google_search],
    output_key="carbon_capture_result"
)

# 병렬 에이전트(ParallelAgent): 동시 연구 진행
parallel_research_agent = ParallelAgent(
    name="ParallelWebResearchAgent",
    sub_agents=[researcher_agent_1, researcher_agent_2, researcher_agent_3],
    description="여러 연구 에이전트를 병렬로 실행하여 정보를 수집합니다."
)

# 병합 에이전트: 병렬 에이전트들이 세션 상태에 저장한 결과들을 취합하여 하나의 구조화된 보고서로 종합.
merger_agent = LlmAgent(
    name="SynthesisAgent",
    model="gemini-2.5-flash",
    instruction="""당신은 연구 결과를 구조화된 보고서로 결합하는 AI 도우미입니다.
    당신의 주요 임무는 다음 연구 요약들을 종합하여, 각 발견의 출처 영역을 명확히 밝히는 것입니다.
    각 주제별로 제목을 사용하여 응답을 구조화하세요. 보고서가 일관성 있고 핵심 내용을 매끄럽게 통합하도록 하세요.

    결정적으로 당신의 전체 응답은 오직 아래 'SUMMARY'에 제공된 정보에만 기반해야 합니다.
    여기에 없는 외부 지식, 사실, 또는 세부 사항을 추가하지 마세요.
    반드시 아래의 OUTPUT_FORMAT에 따라 보고서를 생성하세요.

    SUMMARY:
    *   **신재생 에너지:** {renewable_energy_result}
    *   **전기차:** {ev_technology_result}
    *   **탄소 포집:** {carbon_capture_result}

    OUTPUT_FORMAT:
    ## 최신 지속 가능한 기술 발전 요약
    ### 신재생 에너지 연구 결과
    (위에서 제공된 신재생 에너지 SUMMARY에 대해서 종합하여 설명하세요.)

    ### 전기차 연구 결과
    (위에서 제공된 전기차 SUMMARY에 대해서 종합하여 설명하세요.)

    ### 탄소 포집 연구 결과
    (위에서 제공된 탄소 포집 SUMMARY에 대해서 종합하여 설명하세요.)

    ### 전반적인 결론
    (위에서 제공된 전체 연구 결과에 대해서 짧게 1~2줄로 종합하여 요약하세요.)
    """,
    description="병렬 에이전트의 연구 결과를 구조화된 보고서로 결합하고, 제공된 입력에 엄격히 근거합니다.",
)

# 순차 에이전트(SequentialAgent): 전체 순차 파이프라인
root_agent = SequentialAgent(
    name="ResearchSynthesisPipeline",
    sub_agents=[parallel_research_agent, merger_agent], # 병렬 연구 먼저 실행, 그 다음 병합
    description="병렬 연구를 조율하고 결과를 종합합니다."
)