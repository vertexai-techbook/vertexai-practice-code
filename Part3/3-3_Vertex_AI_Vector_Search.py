# == 2. Vertex AI Embeddings를 활용한 임베딩 생성 == #
import json
import os
from typing import List, Dict, Optional
from faq import faq_data_raw

import vertexai
from google import genai
from google.genai.types import EmbedContentConfig

PROJECT_ID = "vertexai-books"
LOCATION = "asia-northeast3"

# 클라이언트 초기화
vertexai.init(project=PROJECT_ID, location=LOCATION)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Vertex AI Embeddings 모델을 활용한 임베딩 생성
def get_embedding_vector(texts: List[str], task_type: str) -> List[List[float]]:
   
    # 1. 임베딩 설정 구성
    embedding_config = EmbedContentConfig(
        task_type=task_type,
        output_dimensionality=768
    )
   
    # 2. 임베딩 요청
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=embedding_config,
    )
    return [emb.values for emb in response.embeddings]

# 데이터 임베딩 및 JSONL 파일 생성
texts_to_embed = [item["text"] for item in faq_data_raw]
document_embeddings = get_embedding_vector(texts_to_embed, "RETRIEVAL_DOCUMENT")

file_path = "faq_embeddings.json"
vector_datapoints = []
for item, emb in zip(faq_data_raw, document_embeddings):
    datapoint = {
        "id": item["id"],
        "embedding": emb,
    }
    vector_datapoints.append(datapoint)
   
with open(file_path, "w") as f:
    for dp in vector_datapoints:
        f.write(json.dumps(dp) + "\n")

# == 2.3. 색인 구축 및 엔드포인트 배포 == #
from google.cloud import aiplatform

INDEX_DISPLAY_NAME = "faq_index"
GCS_INPUT_URI = "gs://mhkim-data-bucket/Vector_Search/FAQ"
DEPLOYED_INDEX_ID = "faq_index_deployed"

faq_index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
    display_name=INDEX_DISPLAY_NAME,
    contents_delta_uri=GCS_INPUT_URI,
    description="FAQ 데이터에 대한 벡터DB 입니다.",
    dimensions=768,
    approximate_neighbors_count=50,
    leaf_node_embedding_count=10,
    leaf_nodes_to_search_percent=20,
distance_measure_type=aiplatform.matching_engine.matching_engine_index_config.DistanceMeasureType.DOT_PRODUCT_DISTANCE,
    index_update_method="BATCH_UPDATE", # 일괄 업데이트 방식 사용
)

# == 2.3.2. 색인 엔드포인트 생성 == #
faq_index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name=f"faq_index_endpoint",
    public_endpoint_enabled=True,
)

# == 2.3.3. 엔드포인트에 색인 배포 == #
faq_index_endpoint.deploy_index(
    index=faq_index,
    deployed_index_id=DEPLOYED_INDEX_ID,
    min_replica_count=1,
)

# == 2.4. 시맨틱 검색 실행 == #
import os
import json
from google.cloud import aiplatform
from google import genai
from google.genai.types import EmbedContentConfig
from typing import List

PROJECT_ID = "vertexai-books"
LOCATION = "asia-northeast3"

# 색인 엔드포인트 ID (Vertex AI 콘솔의 '색인 엔드포인트'에서 확인할 수 있습니다)
INDEX_ENDPOINT_ID = "357809670980632576"

# 배포된 색인 ID (Endpoint에 배포할 때 지정한 고유 ID)
DEPLOYED_INDEX_ID = "faq_index_deployed"

# 유사도 검색에 사용할 사용자 질문
QUERY_TEXT = "고객 센터는 몇 시까지 운영하나요?"

# 클라이언트 초기화
aiplatform.init(project=PROJECT_ID, location=LOCATION)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# 기존 MatchingEngineIndexEndpoint 객체 로드
faq_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=INDEX_ENDPOINT_ID 
)

# 텍스트 임베딩 생성
embedding_config = EmbedContentConfig(
    task_type="RETRIEVAL_QUERY",
    output_dimensionality=768,    # 색인 생성 시 사용된 차원과 반드시 일치
)

response_emb = genai_client.models.embed_content(
    model="gemini-embedding-001",
    contents=[QUERY_TEXT],
    config=embedding_config,
)

# 임베딩 벡터 추출
query_emb: List[float] = response_emb.embeddings[0].values

# 유사도 검색 수행
response = faq_index_endpoint.find_neighbors(
    deployed_index_id=DEPLOYED_INDEX_ID,
    queries=[query_emb],
    num_neighbors=3,
)

# 결과
for neighbor in response[0]:
        print(f"ID: {neighbor.id}, 거리(Distance): {neighbor.distance:.4f}")

# == 3.2 색인 일괄 업데이트 == #
from google.cloud import aiplatform

UPDATED_GCS_URI = "gs://mhkim-data-bucket/Vector_Search/FAQ"
INDEX_ID = "<인덱스 ID>"

faq_index = aiplatform.MatchingEngineIndex(index_name=INDEX_ID)
faq_index.update_embeddings(
    contents_delta_uri=UPDATED_GCS_URI,
    is_complete_overwrite=True
)

# == 4. 필터링을 활용한 검색 결과 제한 == #
import json
import os
from typing import List, Dict, Optional
from faq import faq_data_filtered

import vertexai
from google import genai
from google.genai.types import EmbedContentConfig

PROJECT_ID = "vertexai-books"
LOCATION = "asia-northeast3"

# 클라이언트 초기화
vertexai.init(project=PROJECT_ID, location=LOCATION)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Vertex AI Embeddings 모델을 활용한 임베딩 생성
def get_embedding_vector(texts: List[str], task_type: str) -> List[List[float]]:
   
    # 1. 임베딩 설정 구성
    embedding_config = EmbedContentConfig(
        task_type=task_type,
        output_dimensionality=768
    )
   
    # 2. 임베딩 요청
    response = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=embedding_config,
    )
    return [emb.values for emb in response.embeddings]

# 데이터 임베딩 및 JSONL 파일 생성
texts_to_embed = [item["text"] for item in faq_data_filtered]
document_embeddings = get_embedding_vector(texts_to_embed, "RETRIEVAL_DOCUMENT")

file_path = "faq_filtered_embeddings.json"
vector_datapoints = []
for item, emb in zip(faq_data_raw, document_embeddings):
    datapoint = {
        "id": item["id"],
        "embedding": emb,
        "restricts": [
            {"namespace": "category", "allow": [item["category"]]}
        ]
    }
    vector_datapoints.append(datapoint)

with open(file_path, "w") as f:
    for dp in vector_datapoints:
        f.write(json.dumps(dp) + "\n")

# == 4.2. 필터링을 적용한 쿼리 실행 == #
from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import Namespace

PROJECT_ID = "vertexai-books"
LOCATION = "asia-northeast3"

# 색인 엔드포인트 ID (Vertex AI 콘솔의 '색인 엔드포인트'에서 확인할 수 있습니다)
INDEX_ENDPOINT_ID = "357809670980632576"

# 배포된 색인 ID (Endpoint에 배포할 때 지정한 고유 ID)
DEPLOYED_INDEX_ID = "faq_index_deployed"

# 유사도 검색에 사용할 사용자 질문
QUERY_TEXT = "고객 센터는 몇 시까지 운영하나요?"

# 클라이언트 초기화
aiplatform.init(project=PROJECT_ID, location=LOCATION)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# 기존 MatchingEngineIndexEndpoint 객체 로드
faq_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=INDEX_ENDPOINT_ID 
)

# 텍스트 임베딩 생성
embedding_config = EmbedContentConfig(
    task_type="RETRIEVAL_QUERY",
    output_dimensionality=768,    # 색인 생성 시 사용된 차원과 반드시 일치
)

response_emb = genai_client.models.embed_content(
    model="gemini-embedding-001",
    contents=[QUERY_TEXT],
    config=embedding_config,
)

# 임베딩 벡터 추출
query_emb: List[float] = response_emb.embeddings[0].values

# 필터링 조건 설정
category_filter = [
    Namespace(name="category", allow_tokens=["Support"], deny_tokens=[])
]

# 유사도 검색 수행 (필터링 적용)
response = faq_index_endpoint.find_neighbors(
    deployed_index_id=DEPLOYED_INDEX_ID,
    queries=[query_emb],
    num_neighbors=3,
    filter=category_filter,
)

# 결과
for neighbor in response[0]:
    print(f"ID: {neighbor.id}, 거리(Distance): {neighbor.distance:.4f}")

# == 5.4. 하이브리드 쿼리 실행 == #
import os
from typing import List, Dict, Any
from faq_data import faq_data_filtered

from google.cloud import aiplatform
from google import genai
from google.genai.types import EmbedContentConfig

from google.cloud.aiplatform.matching_engine.matching_engine_index_endpoint import Namespace, HybridQuery, MatchNeighbor

# 희소 벡터 생성을 위한 scikit-learn 라이브러리
from sklearn.feature_extraction.text import TfidfVectorizer

PROJECT_ID = "vertexai-books"
LOCATION = "asia-northeast3"
INDEX_ENDPOINT_ID = "<인덱스 엔드포인트 ID>"
DEPLOYED_INDEX_ID = "faq_filtered_index_deployed"
RRF_ALPHA = 0.5 # 0.5는 밀집(Dense)과 희소(Sparse)에 동등한 가중치를 부여

# 데이터 코퍼스 및 TF-IDF 학습
corpus_data = [item['text'] for item in faq_data_filtered]
faq_map = {item['id']: item['text'] for item in faq_data_filtered}

# TF-IDF Vectorizer 학습
vectorizer = TfidfVectorizer()
vectorizer.fit_transform(corpus_data)

# 클라이언트 초기화
aiplatform.init(project=PROJECT_ID, location=LOCATION)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

faq_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
    index_endpoint_name=INDEX_ENDPOINT_ID
)

# 임베딩 생성
def get_dense_embedding(text: str) -> List[float]:
    """
    gemini-embedding-001 모델을 사용하여 밀집 임베딩을 생성.
    """
    embedding_config = EmbedContentConfig(
        task_type="RETRIEVAL_QUERY",
        output_dimensionality=768,
    )

    response_emb = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=[text],
        config=embedding_config,
    )
   
    query_emb: List[float] = response_emb.embeddings[0].values
    return query_emb

def get_sparse_embedding(text: str) -> Dict[str, List[Any]]:
    """
    학습된 TfidfVectorizer를 사용하여 희소 임베딩을 생성.
    """
    tfidf_vector = vectorizer.transform([text])
   
    values = []
    dims = []

    for i, tfidf_value in enumerate(tfidf_vector.data):
        values.append(float(tfidf_value))
        dims.append(int(tfidf_vector.indices[i]))
    return {"values": values, "dimensions": dims}

# 하이브리드 쿼리 실행
def execute_hybrid_query(
    query_text: str,
    rrf_ranking_alpha: float,
    num_neighbors: int
) -> List[MatchNeighbor]:
   
    # 임베딩
    query_dense_emb = get_dense_embedding(query_text)
    query_sparse_emb_dict = get_sparse_embedding(query_text)
   
    # HybridQuery 객체 생성
    query = HybridQuery(
        dense_embedding=query_dense_emb,
        sparse_embedding_dimensions=query_sparse_emb_dict['dimensions'],
        sparse_embedding_values=query_sparse_emb_dict['values'],
        rrf_ranking_alpha=rrf_ranking_alpha,
    )

    category_filter = [
    Namespace(name="category", allow_tokens=["Billing"], deny_tokens=[])
    ]

    # 유사도 검색 수행
    response = faq_index_endpoint.find_neighbors(
        deployed_index_id=DEPLOYED_INDEX_ID,
        queries=[query],
        num_neighbors=5,
        filter=category_filter
    )
    return response

# 최종 실행 및 결과 출력
QUERY = "결제 취소했는데 환불 언제 돼?"
retrieved_neighbors = execute_hybrid_query(QUERY, RRF_ALPHA, NUM_NEIGHBORS)

for rank, neighbor in enumerate(retrieved_neighbors[0]):
    doc_id = neighbor.id

    # faq_map에서 원본 텍스트를 가져옴.
    text_snippet = faq_map.get(doc_id)
   
    # RRF 점수. (HybridQuery는 RRF 점수를 'distance' 필드에 반환)
    rrf_score = f"{neighbor.distance:.4f}"
   
    # 희소 거리. (반환되지 않는 경우가 많음)
    sparse_dist = f"{neighbor.sparse_distance:.4f}" if hasattr(neighbor, 'sparse_distance') and neighbor.sparse_distance is not None else "N/A"

    print(f"순위: {rank + 1}, ID: {doc_id}, RRF 점수: {rrf_score}, 희소 거리: {sparse_dist}, FAQ: {text_snippet}")
