# == 3.1. 코퍼스 생성 == #
from vertexai import rag
import vertexai

# 클라이언트 초기화
vertexai.init(project="vertexai-books", location="asia-northeast3")

# 벡엔드 임베딩 모델 설정
backend_config = rag.RagVectorDbConfig(
    rag_embedding_model_config=rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-multilingual-embedding-002"
        )
    )
)

corpus = rag.create_corpus(
    display_name="MHAI_Corpus",
    description="사내정보 데이터입니다.",
    backend_config=backend_config,
)
print(corpus)

# == 3.2.1. 로컬 파일 업로드 == #
corpus_name='projects/<프로젝트 넘버>/locations/asia-northeast3/ragCorpora/<코퍼스 ID>'
path='./민형_AI_조직도_및_부서_정보.pdf'

rag_file = rag.upload_file(
    corpus_name=corpus_name,
    path=path,
   
    # 아래 설정은 옵션입니다.
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        ),
    ),
)
print(rag_file)

# == 3.2.2. Google Cloud Storage, Google Drive 파일 업로드 == #
corpus_name='projects/<프로젝트 넘버>/locations/asia-northeast3/ragCorpora/<코퍼스ID>'
paths=['https://drive.google.com/file/d/<파일ID>', 'gs://mhkim-data-bucket/VertexAI_RAG_Engine/민형_AI_사내_생활_가이드_복지.pdf']

# 파일 import
rag_files = rag.import_files(
    corpus_name=corpus_name,
    paths=paths,


    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        ),
    ),
    max_embedding_requests_per_min=1000, # import_files에서만 지정 가능합니다.
)

print(rag_files)

# == 3.3. 검색 == #
response = rag.retrieval_query(
    rag_resources=[
        rag.RagResource(
            rag_corpus=corpus_name,
        )
    ],
    text="2024년 하반기 조직 개편 어떻게 됐어?",
    rag_retrieval_config=rag.RagRetrievalConfig(
        top_k=3,
        filter=rag.utils.resources.Filter(vector_distance_threshold=0.5),
    ),
)
print(response)

# == 3.4 답변 생성 == #
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project='vertexai-books', location='global')

rag_retrieval_tool = [
    types.Tool(
      retrieval=types.Retrieval(
        vertex_rag_store=types.VertexRagStore(
            rag_resources=[
                types.VertexRagStoreRagResource(
                rag_corpus=corpus_name
                )
            ],
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=3,
                filter=rag.utils.resources.Filter(vector_distance_threshold=0.5)
            ),          
        )
      )
    )
]

response = client.models.generate_content(
    model = "gemini-2.5-flash",
    contents = "2024년 하반기 조직 개편 어떻게 됐어?",
    config = types.GenerateContentConfig(tools=rag_retrieval_tool)
)

print(response.text)

# == 4.2. 색인 기반 코퍼스 생성 == #
import vertexai
from vertexai import rag

# Vertex AI init
vertexai.init(project='vertexxai-books', location='asia-northeast3')

vector_search_index_name = "projects/<프로젝트 넘버>/locations/us-central1/indexes/<인덱스ID>"
vector_search_index_endpoint_name = "projects/<프로젝트 넘버>/locations/us-central1/indexEndpoints/<인덱스 엔드포인트ID>"

# 임베딩 모델 설정
embedding_model_config = rag.RagEmbeddingModelConfig(
    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
        publisher_model="publishers/google/models/text-multilingual-embedding-002"
    )
)

# Vertex AI Vector Search 연결
vector_db = rag.VertexVectorSearch(
    index=vector_search_index_name, index_endpoint=vector_search_index_endpoint_name
)

corpus = rag.create_corpus(
    display_name="VertexAI_Vector_Search_Corpus",
    description="Vertex AI Vector Search 인덱스 기반 코퍼스입니다.",
    backend_config=rag.RagVectorDbConfig(
        vector_db=vector_db
    ),
)

print(corpus)

# == 4.3. 데이터 업로드 == #
corpus_name='projects/<프로젝트 넘버>/locations/asia-northeast3/ragCorpora/<코퍼스ID>'

paths=['https://drive.google.com/file/d/<파일ID>', 'gs://mhkim-data-bucket/VertexAI_RAG_Engine/민형_AI_사내_생활_가이드_복지.pdf']

response = rag.import_files(
    corpus_name=corpus_name,
    paths=paths,
    transformation_config=rag.TransformationConfig(
        rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
    max_embedding_requests_per_min=1000,
)

# == 4.4. 검색 == #
response = rag.retrieval_query(
    rag_resources=[
        rag.RagResource(
            rag_corpus=corpus_name,
        )
    ],
    text="2024년 하반기 조직 개편 어떻게 됐어?",
    rag_retrieval_config=rag.RagRetrievalConfig(
        top_k=3,
        filter=rag.utils.resources.Filter(vector_distance_threshold=0.5),
    ),
)

print(response)

# == 4.5. 답변 생성 == #
from vertexai.generative_models import GenerativeModel, Tool

rag_retrieval_tool = Tool.from_retrieval(
    retrieval=rag.Retrieval(
        source=rag.VertexRagStore(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_name,
                )
            ],
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=3,
                filter=rag.utils.resources.Filter(vector_distance_threshold=0.5),
            ),
        ),
    )
)


rag_model = GenerativeModel(
    model_name="gemini-2.5-flash", tools=[rag_retrieval_tool]
)

response = rag_model.generate_content("2024년 하반기 조직 개편 어떻게 됐어?")
print(response.text)

# == 5.1. 앱 기반 코퍼스 생성 == #
import vertexai
from vertexai import rag

# Vertex AI init
vertexai.init(project='vertexxai-books', location='asia-northeast3')

vertex_ai_search_engine_name = "projects/<프로젝트ID>/locations/global/collections/default_collection/engines/<앱ID>"

# Vertex AI Search 연결
vertex_ai_search_config = rag.VertexAiSearchConfig(
    serving_config=f"{vertex_ai_search_engine_name}/servingConfigs/default_search"
)

corpus = rag.create_corpus(
    display_name="VertexAI_Search_Corpus",
    description="Vertex AI Search 앱 기반 코퍼스입니다.",
    vertex_ai_search_config=vertex_ai_search_config,
)

# == 5.2. 검색 == #
corpus_name='projects/<프로젝트 넘버>/locations/asia-northeast3/ragCorpora/<코퍼스ID>'


response = rag.retrieval_query(
    rag_resources=[
        rag.RagResource(
            rag_corpus=corpus_name,
        )
    ],
    text="전기차 얼마까지 주행 가능해?",
    rag_retrieval_config=rag.RagRetrievalConfig(
        top_k=3,
        filter=rag.utils.resources.Filter(vector_distance_threshold=0.5),
    ),
)
print(response)

# == 5.3. 답변 생성 == #
from google import genai
from google.genai import types

client = genai.Client(vertexai=True, project='vertexai-books', location='global')

rag_retrieval_tool = [
    types.Tool(
        retrieval=types.Retrieval(
        vertex_rag_store=types.VertexRagStore(
            rag_resources=[
            types.VertexRagStoreRagResource(
                rag_corpus=corpus_name
            )
            ],
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=3,
                filter=rag.utils.resources.Filter(vector_distance_threshold=0.5),          
            )
        )
        )
    )
]

response = client.models.generate_content(
    model = "gemini-2.5-flash",
    contents = "전기차 얼마까지 주행 가능해?",
    config = types.GenerateContentConfig(tools=rag_retrieval_tool)
)

print(response.text)

