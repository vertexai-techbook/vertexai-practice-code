# vertexai-practice-code

「Vertex AI와 Gemini로 시작하는 생성형 AI 실전 개발」의 예제 코드입니다.
본 저장소는 독자분들이 책의 실습을 편히 따라 하실 수 있도록 예제 파일들을 제공합니다.

## 📌 안내 사항

- **포함된 내용**: 책에서 사용된 **Python 코드, SQL Query문, YAML 파일** 등 실습에 필요한 소스 코드 들이 포함되어 있습니다.
- **제외된 내용**: 책 본문에서 설명하는 **시스템 프롬프트**나 사용된 데이터, 터미널에서 실행하는 **CLI 명령어** 등은 포함되어 있지 않으므로 책 본문을 함께 참고해 주시기 바랍니다.

### ⚠️ [긴급] API Key 기반 Gemini API(Gemini Developer API) 과금 방식 전면 개편 안내 (2026년 4월 1일~)     

> Google이 Gemini API 과금 방식을 전면 개편하며, **2026년 4월 1일부터** 적용됩니다. 모든 결제 계정에 사용 티어에 연동된 **월간 지출 한도가 강제 적용**되고, 신규 사용자는 선불 결제를 이용해야 하며, 전체 티어 자격 시스템이 더 낮은 기준으로 재구성되었습니다. 본 책의 **APPENDIX**에서 다루는 내용과 관련되므로 아래 사항을 꼭 확인해 주세요.

#### 티어별 강제 월 지출 한도

한도에 도달하면 해당 빌링 계정의 **모든 API 요청이 다음 빌링 주기까지 자동 중단**됩니다.

| 티어 | 월 지출 한도 |
|------|------------|
| **Tier 1** | **$250** |
| **Tier 2** | **$2,000** |
| **Tier 3** | **$20,000 ~ $100,000+** (계정 상태에 따라 다름) |       

#### 사용 티어 자동 업그레이드

기존에는 상위 티어 진입 조건이 까다로웠으나, 이번에 전면 개편되었습니다.

- 상위 티어 진입을 위한 **최소 지출 기준이 낮아졌고**, 조건을 충족하면 **자동으로 다음 티어로 업그레이드**됩니다.
- 수동 신청 없이 더 높은 요청 한도와 월간 쿼터를 바로 쓸 수 있게       
됩니다.
- 각 티어에는 **전체 빌링 계정 단위의 최대 지출 상한**이 생겼고, 티어가
 올라갈수록 상한도 자동으로 높아집니다.

#### 프로젝트별 월 한도 직접 설정

- Google AI Studio의 **Spend 탭**에서 프로젝트 단위 월별 상한선을      
설정할 수 있습니다.
- 여러 프로젝트를 동시에 운영하는 개발자나 팀에게 특히 유용합니다.     
실험용 프로젝트는 낮게, 프로덕션은 여유 있게 설정하는 식으로
프로젝트마다 다른 예산 기준을 적용할 수 있습니다.
- 다만 한도 적용에 약 **10분 정도의 지연**이 있어, 그 사이 발생한 초과      
비용은 사용자 책임으로 처리됩니다.

#### 비용 파악도 더 쉽게

- **요금 대시보드**: 프로젝트별 일별 비용을 최근 7일~한 달 단위로      
추적할 수 있고, 모델별 필터링도 됩니다.
- **Rate Limit 대시보드**: 분당 요청 수(RPM), 분당 토큰 수(TPM), 일일  
요청 수(RPD) 세 가지 지표를 실시간으로 보여주며, 트래픽 급증 구간을    
시각적으로 파악할 수 있습니다.

#### 필요한 조치

- **사용량 모니터링**: [Google AI
Studio](https://aistudio.google.com)에 로그인하여 월별 지출 한도를     
확인하고 현재 사용량을 모니터링하세요.
- **한도 상향 요청**: 현재 할당된 한도를 초과하는 즉각적인 사용량      
증가가 예상되는 경우 [이
양식](https://ai.google.dev/gemini-api/docs/rate-limits)을 작성하여    
맞춤 한도 상향을 요청하세요.

> 자세한 내용은 [Gemini API Rate Limits 공식
문서](https://ai.google.dev/gemini-api/docs/rate-limits?hl=ko)를 참고해
 주세요.

## 📋 필요 패키지 설치

본 실습 환경을 구성하기 위해 필요한 패키지 설치 방법입니다.

### 1) 공통 필수 패키지 및 라이브러리
대부분의 실습 파트(Part 1 ~ Part 7) 파이썬 코드를 실행하기 위해서 기본적으로 다음 패키지가 필요합니다. Google GenAI SDK와 Vertex AI Python SDK 입니다.
```bash
pip install google-genai google-cloud-aiplatform
```

### 2) 작업별 추가 패키지 설치
특정 파트의 실습을 수행하기 위해 설치해야할 패키지입니다.

- **`Part4. 스스로 생각하고 행동하는 AI - 맞춤형 AI 에이전트 개발`의 MCP 및 ADK, MCP Toolbox for Databases 실습**
  ```bash
  pip install mcp google-adk python-dotenv toolbox-core
  ```

- **`Part6. 엔터프라이즈 AI - 차세대 에이전트 아키텍처와 통합 AI 플랫폼`의 MCP 및 LangGraph, A2A 실습**
  ```bash
  pip install a2a-sdk uvicorn jq fastmcp langgraph langchain-core langchain-google-vertexai langchain-mcp-adapters langchain-mcp-adapters
  ```

---

## 📂 디렉터리 및 주요 파일 구조

### Part 1

- `1-3_Gemini_API.py`
- `1-4_Tuning.py`

### Part 2

- `2-2_Vertex_AI_Prompt_Management.py`

### Part 3

- `3-2_Vertex_AI_Embeddings.py`
- `3-3_Vertex_AI_Vector_Search.py`
- `3-4_Vertex_AI_Search.py`
- `3-5_Vertex_AI_RAG_Engine.py`
- `3-6_Gemini_File_Search.py`

### Part 4

- `4-1_Function_Calling.py`
- `4-2_Google_Built-in_Tools.py`
- `4-3_MCP(Model_Context_Protocol).py`
- `4-4_ADK(Agent-Development-Kit)/`
  - `ex1_Simple_Agent/`
  - `ex2_ToolContext_Artifacts/`
  - `ex3_sequential_loop_agent/`
  - `ex4_sequential_parallel_agent/`
  - `ex5_Multiturn_Chat_Agent/`
  - `ex6_Deploy_Agent/`
  - `ex7_MCP_Agent/`
  - `ex8_Evaluation/`
- `4-6_MCP_Toolbox_for_Databases/`
  - `6_DB_에이전트_개발.py`
  - `toolbox.yaml`
- `4-7_Conversational_Agents/`
  - `main.py`
  - `bigquery_schema.sql`
  - `dialogflow_messanger.html`
  - `schema.yaml`

### Part 5

- `5-1_Google_BigQuery.sql`
- `5-2_BigQuery_ML.sql`
- `5-3_BigQuery_Vector_Search.sql`

### Part 6

- `6-1_A2A(Agent-to-Agent).py`
- `3_3_A2A_MCP_LangGraph/`
  - `agent.py`
  - `mcp_server.py`
  - `Dockerfile`

### Part 7

- `7-1_Gemini_Multimodal_Contents_Understanding.py`
- `7-2_Gemini_Multimodal_Contents_Generate.py`

---

## 📚 참고 문헌

### Part 1. 시작하기 - Google Cloud Vertex AI와 생성형 AI 개요

- [Gemini API Text Generation](https://ai.google.dev/gemini-api/docs/text-generation)
- [Gemini Thinking](https://ai.google.dev/gemini-api/docs/thinking)
- [Gemini Models](https://ai.google.dev/gemini-api/docs/models)
- [Gemini API Release Note](https://ai.google.dev/gemini-api/docs/changelog)
- [Gemini Model Deprecations](https://ai.google.dev/gemini-api/docs/deprecations)
- [Gemini Developer API vs Vertex AI](https://ai.google.dev/gemini-api/docs/migrate-to-cloud)
- [Generative AI on Vertex AI](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/overview)
- [Google Cloud IAM](https://docs.cloud.google.com/iam/docs)
- [Google Cloud Storage](https://docs.cloud.google.com/storage/docs)

### Part 2. LLM과의 대화법 - 프롬프트 엔지니어링 및 관리

- [Prompt Engineering](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-design-strategies)
- [Vertex AI Prompt Management](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/prompt-classes)

### Part 3. 지식 기반 확장 - 나만의 지식을 학습한 AI 시스템 구축

- [Vertex AI Embeddings](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/embeddings)
- [Vertex AI Vector Search](https://docs.cloud.google.com/vertex-ai/docs/vector-search/overview)
- [Vertex AI Search](https://docs.cloud.google.com/generative-ai-app-builder/docs)
- [Vertex AI RAG Engine](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)

### Part 4. 스스로 생각하고 행동하는 AI - 맞춤형 AI 에이전트 개발

- [Gemini Function Calling](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/function-calling)
- [Google Built-in Tools](https://ai.google.dev/gemini-api/docs/tools)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/docs/getting-started/intro)
- [Google ADK](https://google.github.io/adk-docs/)
- [MCP Toolbox for Databases](https://googleapis.github.io/genai-toolbox/getting-started/introduction/)
- [Conversational Agents](https://docs.cloud.google.com/dialogflow/cx/docs/concept/console-conversational-agents)

### Part 5. 플랫폼 확장 - BigQuery와 Gemini의 통합 활용 전략

- [Google BigQuery](https://docs.cloud.google.com/bigquery/docs)
- [BigQuery ML](https://docs.cloud.google.com/bigquery/docs/bqml-introduction)
- [BigQuery Generative AI functions](https://docs.cloud.google.com/bigquery/docs/generative-ai-overview)
- [BigQuery Vector Search](https://docs.cloud.google.com/bigquery/docs/vector-search-intro)

### Part 6. 엔터프라이즈 AI - 차세대 에이전트 아키텍처와 통합 AI 플랫폼

- [A2A Protocol](https://a2a-protocol.org/latest/)
- [Gemini Enterprise](https://docs.cloud.google.com/gemini/enterprise/docs)

### Part 7. 텍스트를 넘어서 - 이미지, 영상, 음성을 아우르는 Gemini

- [Gemini Image Understanding](https://ai.google.dev/gemini-api/docs/image-understanding)
- [Gemini Video Understanding](https://ai.google.dev/gemini-api/docs/video-understanding)
- [Gemini Audio Understanding](https://ai.google.dev/gemini-api/docs/audio)
- [Gemini Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini Video Generation](https://ai.google.dev/gemini-api/docs/video)
- [Gemini Speech Generation](https://ai.google.dev/gemini-api/docs/speech-generation)

### APPENDIX

- [Vertex AI PayGo](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/standard-paygo)
- [Vertex AI Provisioned Throughput](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput/overview)
- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Gen AI Evaluation Service](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview)
- [Model Armor](https://docs.cloud.google.com/model-armor)
