-- 1.1 임베딩 생성
CREATE OR REPLACE MODEL `vertexai_books_ds.text-embed-model`
REMOTE WITH CONNECTION `vertexai-books.us-central1.gemini-conn`
OPTIONS (ENDPOINT = 'text-multilingual-embedding-002');

CREATE OR REPLACE TABLE vertexai_books_ds.hr_policies_embeddings AS
SELECT * FROM ML.GENERATE_EMBEDDING(
  MODEL `vertexai-books.vertexai_books_ds.text-embed-model`,
  (SELECT content, title from vertexai_books_ds.hr_policies),
  STRUCT(TRUE AS flatten_json_output,
    'RETRIEVAL_DOCUMENT' AS task_type,
    768 AS output_dimensionality)
);

-- 1.2. 유사도 검색
DECLARE question STRING DEFAULT '휴가 신청은 어떻게 해?';

SELECT query.query, base.title, base.content, distance
FROM VECTOR_SEARCH(
  TABLE `vertexai_books_ds.hr_policies_embeddings`, 'ml_generate_embedding_result',
  (
  SELECT ml_generate_embedding_result, content AS query
  FROM ML.GENERATE_EMBEDDING(
  MODEL `vertexai_books_ds.text-embed-model`,
  (SELECT question AS content))
  ),
  top_k => 3)

-- 1.3. 답변 생성
-- 1.파싱된 응답만 출력(flatten_json_output = TRUE)
DECLARE question STRING DEFAULT '휴가 신청은 어떻게 해?';

SELECT ml_generate_text_llm_result AS generated, prompt
FROM ML.GENERATE_TEXT(
  MODEL `vertexai_books_ds.gemini-model`,
  (
    SELECT CONCAT(
      '당신은 친절한 사내 인사규정 안내 챗봇입니다. 아래에 제공된 [참고 문서]만을 바탕으로 사용자의 [질문]에 대해 답변해주세요. \n\n[참고문서]',
      STRING_AGG(
        FORMAT("\n규정 제목: %s, \n규정 내용: %s \n[질문]\n %s", base.title, base.content, question))
      ) AS prompt,
    FROM VECTOR_SEARCH(
      TABLE `vertexai_books_ds.hr_policies_embeddings`, 'ml_generate_embedding_result',
      (
        SELECT ml_generate_embedding_result, content AS query
        FROM ML.GENERATE_EMBEDDING(
          MODEL `vertexai_books_ds.text-embed-model`,
         (SELECT question AS content)
        )
      ),
    top_k => 3)
  ),
  STRUCT(8192 AS max_output_tokens, TRUE AS flatten_json_output));

-- 2.원본 JSON 응답 출력(flatten_json_output = FALSE)
DECLARE question STRING DEFAULT '휴가 신청은 어떻게 해?';

SELECT ml_generate_text_result AS generated, prompt
FROM ML.GENERATE_TEXT(
  MODEL `vertexai_books_ds.gemini-model`,
  (
    SELECT CONCAT(
      '당신은 친절한 사내 인사규정 안내 챗봇입니다. 아래에 제공된 [참고 문서]만을 바탕으로 사용자의 [질문]에 대해 답변해주세요. \n\n[참고문서]',
      STRING_AGG(
        FORMAT("\n규정 제목: %s, \n규정 내용: %s \n[질문]\n %s", base.title, base.content, question))
      ) AS prompt,
    FROM VECTOR_SEARCH(
      TABLE `vertexai_books_ds.hr_policies_embeddings`, 'ml_generate_embedding_result',
      (
        SELECT ml_generate_embedding_result, content AS query
        FROM ML.GENERATE_EMBEDDING(
          MODEL `vertexai_books_ds.text-embed-model`,
         (SELECT question AS content)
        )
      ),
    top_k => 3)
  ),
  STRUCT(8192 AS max_output_tokens, FALSE AS flatten_json_output));

-- 1.4. (선택사항) 벡터 색인 만들기
CREATE OR REPLACE VECTOR INDEX my_index
ON `vertexai_books_ds.hr_policies_embeddings`(ml_generate_embedding_result)
OPTIONS(index_type = 'IVF',
  distance_type = 'COSINE',
  ivf_options = '{"num_lists":500}')

-- 2.1. 객체 테이블 생성
CREATE OR REPLACE EXTERNAL TABLE vertexai_books_ds.fashion_images
WITH CONNECTION `vertexai_books.us-central1.gemini-conn`
OPTIONS
 ( object_metadata = 'SIMPLE',
   uris = ['gs://mhkim-data-bucket/BQ_Vector_Search/images/*']
 );

-- 2.2. 임베딩 생성
CREATE OR REPLACE MODEL `vertexai_books_ds.image-embed-model`
REMOTE WITH CONNECTION `vertexai-books.us-central1.gemini-conn`
OPTIONS (ENDPOINT = 'multimodalembedding@001');

CREATE OR REPLACE TABLE vertexai_books_ds.fashion_images_embeddings
AS
SELECT *
FROM ML.GENERATE_EMBEDDING(
  MODEL `vertexai_books_ds.image-embed-model`,
  (SELECT * FROM `vertexai_books_ds.fashion_images` limit 5000)
);

-- 2.3. 유사도 검색
SELECT
  query.query,
  base.uri,
  distance
FROM
  VECTOR_SEARCH(
    TABLE `vertexai_books_ds.fashion_images_embeddings`,
    'ml_generate_embedding_result',
    (
      SELECT
        ml_generate_embedding_result,
        content AS query
      FROM
        ML.GENERATE_EMBEDDING(
          MODEL `vertexai_books_ds.image_embed_model`,
          (SELECT '꽃무늬 패턴의 빨간 드레스' AS content)
        )
    ),
    top_k => 5,
    distance_type => 'COSINE'
  );