# == 5.1. Answer API를 활용한 RAG 구현 == #
import requests
import subprocess

PROJECT_ID = "vertexai-books"
ENGINE_ID = "article-search-app"

def get_access_token():
    """gcloud 명령어로 인증 토큰 가져오기"""
    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def answer(query, project_id, engine_id):
    """
    1단계: Answer API 호출
    Vertex AI Search의 '답변으로 검색' API를 호출합니다.
    """
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:answer"
   
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }
   
    data = {
        "query": {
            "text": query,
        },
        "answerGenerationSpec": {
            "includeCitations": True,
            "modelSpec": {"modelVersion": "stable"},
            "promptSpec": {"preamble": "답변할 때 앞에 항상 '민형 AI의 검색 결과입니다.'는 문구를 붙여줘."}
        },    
    }
   
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def extract_result(answer_response):
    """
    2단계: 필요한 정보만 추출
    답변 텍스트, 참고 기사를 추출합니다.
    """
    answer_data = answer_response.get('answer', {})
   
    # 1. 답변 텍스트 추출
    answer_text = answer_data.get('answerText', '')
   
    # 2. 답변에 참고된 기사 추출
    # 2-1. citations에서 실제 참고된 referenceId 수집 (중복 제거)
    referenced_ids = set()
    citations = answer_data.get('citations', [])
   
    for citation in citations:
        sources = citation.get('sources', [])
        for source in sources:
            ref_id = source.get('referenceId')
            referenced_ids.add(int(ref_id))
   
    # 2-2. steps에서 검색 결과 전체 리스트 가져오기
    search_results = []
    steps = answer_data.get('steps', [])
   
    for step in steps:
        actions = step.get('actions', [])
        for action in actions:
            observation = action.get('observation', {})
            results = observation.get('searchResults', [])
            search_results.extend(results)
   
    # 2-3. referenceId에 해당하는 기사만 필터링 (순서 유지)
    references = []
    sorted_ref_ids = sorted(list(referenced_ids))
   
    for ref_id in sorted_ref_ids:
        if ref_id < len(search_results):
            result = search_results[ref_id]
            struct_data = result.get('structData', {})
           
            if struct_data:
                references.append({
                    'id': struct_data.get('id'),
                    'text': struct_data.get('text'),
                    'published_time': struct_data.get('published_time')
                })
   
    return {
        '답변': answer_text,
        '참고기사': references
    }


def get_rag_answer(query, project_id, engine_id):
    """
    RAG 실행
    """
   
    # 1단계: 답변 생성
    answer_response = answer(query, project_id, engine_id)

    # 2단계: 필요 정보 추출
    result = extract_result(answer_response)
   
    return result

if __name__ == "__main__":
   
    # 사용자 질문
    user_question = "AI 시대에 개발자 전망은 어떄?"
   
    # RAG 실행
    result = get_rag_answer(user_question, PROJECT_ID, ENGINE_ID)
    print(result)


# == 5.3. Search API와 Answer API 각각 구현 == #
def search(query, project_id, engine_id):
    """
    1단계: Search API 호출
    사용자 질문으로 관련 문서를 검색합니다.
    """
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:search"
   
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }
   
    data = {
        "query": query,
        "session": f"projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}/sessions/-"
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def extract_session_info(search_response):
    """
    2단계: 세션 정보 추출
    검색 결과에서 세션 ID와 쿼리 ID를 추출합니다.
    """
    session_info = search_response.get('sessionInfo', {})
    session_name = session_info.get('name')
    query_id = session_info.get('queryId')
   
    return session_name, query_id

def answer(query, session_name, query_id, project_id, engine_id):
    """
    3단계: Answer API 호출
    추출한 세션 정보로 AI 답변을 생성합니다.
    """
    url = f"https://discoveryengine.googleapis.com/v1alpha/projects/{project_id}/locations/global/collections/default_collection/engines/{engine_id}/servingConfigs/default_search:answer"
   
    headers = {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json"
    }
   
    data = {
        "query": {
            "text": query,
            "queryId": query_id
        },
        "session": session_name,
        "answerGenerationSpec": {
            "includeCitations": True,
            "modelSpec": {"modelVersion": "stable"},
            "promptSpec": {"preamble": "답변할 때 앞에 항상 '민형 AI의 검색 결과입니다.'는 문구를 붙여줘."}
        }
    }
   
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def extract_result(answer_response):
    """
    2단계: 필요한 정보만 추출
    답변 텍스트, 참고 기사를 추출합니다.
    """
    answer_data = answer_response.get('answer', {})
   
    # 1. 답변 텍스트 추출
    answer_text = answer_data.get('answerText', '')
   
    # 2. 답변에 참고된 기사 추출
    # 2-1. citations에서 실제 참고된 referenceId 수집 (중복 제거)
    referenced_ids = set()
    citations = answer_data.get('citations', [])
   
    for citation in citations:
        sources = citation.get('sources', [])
        for source in sources:
            ref_id = source.get('referenceId')
            referenced_ids.add(int(ref_id))
   
    # 2-2. steps에서 검색 결과 전체 리스트 가져오기
    search_results = []
    steps = answer_data.get('steps', [])
   
    for step in steps:
        actions = step.get('actions', [])
        for action in actions:
            observation = action.get('observation', {})
            results = observation.get('searchResults', [])
            search_results.extend(results)
   
    # 2-3. referenceId에 해당하는 기사만 필터링 (순서 유지)
    references = []
    sorted_ref_ids = sorted(list(referenced_ids))
   
    for ref_id in sorted_ref_ids:
        if ref_id < len(search_results):
            result = search_results[ref_id]
            struct_data = result.get('structData', {})
           
            if struct_data:
                references.append({
                    'id': struct_data.get('id'),
                    'text': struct_data.get('text'),
                    'published_time': struct_data.get('published_time')
                })
   
    return {
        '답변': answer_text,
        '참고기사': references
    }

def get_rag_answer(query, project_id, engine_id):
    """
    RAG 전체 프로세스 실행
    검색 → 세션 추출 → 답변 생성
    """
    # 1단계: 검색
    search_response = search(query, project_id, engine_id)
   
    # 2단계: 세션 정보 추출
    session_name, query_id = extract_session_info(search_response)
   
    # 3단계: 답변 생성
    answer_response = answer(query, session_name, query_id, project_id, engine_id)

    # 4단계: 필요 정보 추출
    result = extract_result(answer_response)
   
    return result

if __name__ == "__main__":
   
    # 사용자 질문
    user_question = "AI 시대에 개발자 전망은 어떄?"
   
    # RAG 실행
    result = get_rag_answer(user_question, PROJECT_ID, ENGINE_ID)
    print(result)

# == 6.1. 빈 데이터 스토어 생성 == #
def create_data_store(project_id, data_store_id, display_name):
    """
    1단계: 빈 데이터 스토어 생성 (POST)
    """
    url = f"https://discoveryengine.googleapis.com/v1/projects/{project_id}/locations/global/collections/default_collection/dataStores?dataStoreId={data_store_id}"
   
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_ID
    }
   
    # 요청 바디 구성
    data = {
        "displayName": display_name,
        "industryVertical": 'GENERIC'
    }
   
    print(f"[{data_store_id}] 데이터 스토어 생성 요청 중...")
    response = requests.post(url, headers=headers, json=data)
   
    if response.status_code == 200:
        print("데이터 스토어 생성 작업이 시작되었습니다.")
        return response.json()
    else:
        print(f"데이터 스토어 생성 실패: {response.status_code}")
        print(response.text)
        return None

# == 6.2. 스키마 정의 및 업데이트 == #
def update_schema(project_id, data_store_id):
    """
    2단계: 스키마 정의 및 업데이트 (Patch)
    id, text, published_time -> 모두 string
    """
                       
    url = f"https://discoveryengine.googleapis.com/v1beta/projects/{project_id}/locations/global/collections/default_collection/dataStores/{data_store_id}/schemas/default_schema"
   
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
   
    # 스키마 정의
    schema_payload = {
        "structSchema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "retrievable": True,  # 검색 결과에 표시
                    "indexable": True     # 필터링 가능
                },
                "text": {
                    "type": "string",
                    "retrievable": True,
                    "searchable": True    # 본문 검색(키워드 매칭) 허용
                },
                "published_time": {
                    "type": "string",
                    "retrievable": True,
                    "indexable": True
                }
            }
        }
    }
   
    print(f"[{data_store_id}] 스키마 업데이트 요청 중...")
    response = requests.patch(url, headers=headers, json=schema_payload)
   
    if response.status_code == 200:
        print("스키마 업데이트 성공.")
        return response.json()

if __name__ == "__main__":
    # 1. 데이터 스토어 생성
    creation_result = create_data_store(PROJECT_ID, DATA_STORE_ID, DISPLAY_NAME)

    # 2. 스키마 업데이트 실행
    update_schema(PROJECT_ID, DATA_STORE_ID)
