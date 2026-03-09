# == 2. 텍스트 임베딩 생성하기 == #
from google import genai
from google.genai.types import EmbedContentConfig

# 클라이언트 초기화
client = genai.Client(vertexai=True, project="vertexai-books", location="global")

# 임베딩할 텍스트
texts_to_embed = [
    "운전면허증을 어떻게 받나요?",
    "운전면허증은 얼마나 오랫동안 유효한가요?",
    "운전면허 지식 테스트 학습 가이드"
]

# (Optional) 임베딩 설정 구성
embedding_config = EmbedContentConfig(
    task_type="RETRIEVAL_DOCUMENT",
    output_dimensionality=768, # 차원을 768로 지정하여 저장 공간 절약 가능
)

# 임베딩 생성 요청
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=texts_to_embed,
    # config=embedding_config, 설정하지 않을 시 Default 차원: 3072
)

# 결과 출력
print(f"생성된 임베딩 개수: {len(response.embeddings)}")

print(response.embeddings)

# == 3. 멀티모달 임베딩 생성하기 == #
import vertexai
from vertexai.vision_models import Image, MultiModalEmbeddingModel


# 클라이언트 초기화
vertexai.init(project="vertexai-books", location="asia-northeast3")

# 모델 로드 및 입력 데이터 정의
model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")
image_uri = "gs://mhkim-data-bucket/VertexAI_Books/Tower-Eiffel.jpg" # Cloud Storage 이미지 경로
image_input = Image.load_from_file(image_uri)
text_context = "Tower-Effel" # 이미지와 관련된 텍스트 컨텍스트

# 임베딩 생성 (기본 1408 차원)
embeddings = model.get_embeddings(
    image=image_input,
    contextual_text=text_context,
    dimension=1408,
)

# 결과 출력
print("--- 이미지 및 텍스트 임베딩 결과 ---")
print(f"이미지 임베딩 길이: {len(embeddings.image_embedding)}")
print(f"텍스트 임베딩 길이: {len(embeddings.text_embedding)}")
print(f"이미지 임베딩 벡터: {embeddings.image_embedding}")
print(f"텍스트 임베딩 벡터: {embeddings.text_embedding}")