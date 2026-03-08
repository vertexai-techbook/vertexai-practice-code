-- 2.1.1. 데이터 탐색
SELECT
  species,
  island,
  culmen_length_mm,
  culmen_depth_mm,
  flipper_length_mm,
  body_mass_g,
  sex
FROM
  `bigquery-public-data.ml_datasets.penguins`
WHERE
  body_mass_g IS NOT NULL
LIMIT 10;

-- 2.1.2. 모델 생성 (CREATE MODEL)
CREATE OR REPLACE MODEL `bqml_test.penguin_weight_model`
OPTIONS
  (model_type='LINEAR_REG', input_label_cols=['body_mass_g']) AS
SELECT
  culmen_length_mm,
  culmen_depth_mm,
  flipper_length_mm,
  species,
  island,
  sex,
  body_mass_g
FROM
  `bigquery-public-data.ml_datasets.penguins`
WHERE
  body_mass_g IS NOT NULL;

-- 2.1.3. 모델 평가 (ML.EVALUATE)
SELECT
  *
FROM
  ML.EVALUATE(MODEL `bqml_test.penguin_weight_model`,
    (
    SELECT
      culmen_length_mm,
      culmen_depth_mm,
      flipper_length_mm,
      species,
      island,
      sex,
      body_mass_g
    FROM
      `bigquery-public-data.ml_datasets.penguins`
    WHERE
      body_mass_g IS NOT NULL
    )
  );

-- 2.1.4 예측 수행 (ML.PREDICT)
SELECT
  *
FROM
  ML.PREDICT(MODEL `bqml_test.penguin_weight_model`,
    (
    SELECT
      species,
      island,
      culmen_length_mm,
      culmen_depth_mm,
      flipper_length_mm,
      sex,
      body_mass_g -- 실제값과 비교하기 위해 포함
    FROM
      `bigquery-public-data.ml_datasets.penguins`
    WHERE
      body_mass_g IS NOT NULL
    LIMIT 10
    )
  );

-- 3. BigQuery ML로 Gemini 사용해보기

-- 3.3.1. AI.GENERATE
SELECT
  title,
  AI.GENERATE(
    ('Summarize the movie', title, 'in two short sentences in korean.'),
    connection_id => 'us-central1.gemini-conn',
    endpoint => 'gemini-2.5-flash').result
FROM vertexai_books_ds.movie;

-- 3.3.2. AI.GENERATE(Structured Output)
SELECT
  title,
  AI.GENERATE(
    ('What is the genre of movie ', title, '?'),
    connection_id => 'us-central1.gemini-conn',
    endpoint => 'gemini-2.5-flash',
    output_schema => 'movie STRING, genre STRING').genre
FROM vertexai_books_ds.movie;

-- 3.3.3. AI.GENERATE_BOOL
SELECT
  title,
  AI.GENERATE_BOOL(
    ('Is the movie ', title, ' classified as science fiction?'),
    connection_id => 'us-central1.gemini-conn',
    endpoint => 'gemini-2.5-flash').result
FROM vertexai_books_ds.movie;

-- 3.3.4. AI.GENERATE_INT / AI.GENERATE_DOUBLE
SELECT
  title,
  AI.GENERATE_INT(
    ('What is the approximate runtime in minutes for the movie? ', title),
    connection_id => 'us-central1.gemini-conn',
    endpoint => 'gemini-2.5-flash').result
FROM vertexai_books_ds.movie;

SELECT
  title,
  AI.GENERATE_DOUBLE(
    ('What is the average critical rating out of 10.0 for the movie? ', title),
    connection_id => 'us-central1.gemini-conn',
    endpoint => 'gemini-2.5-flash').result
FROM vertexai_books_ds.movie;

-- 3.3.5. AI.GENERATE_TABLE
CREATE OR REPLACE MODEL `vertexai-books.vertexai_books_ds.gemini-model`
REMOTE WITH CONNECTION `vertexai-books.us-central1.gemini-conn`
OPTIONS (ENDPOINT = 'gemini-2.5-flash');

CREATE OR REPLACE TABLE
  `vertexai_books_ds.movie-metadata`

AS
  SELECT
    actor_name,
    character_name,
    notable_quotes
  FROM
    AI.GENERATE_TABLE(
      MODEL `vertexai_books_ds.gemini-model`,
      (
        SELECT
          ('Generate a table of the main actors, their characters, and memorable lines from at least two movies: ', title) AS prompt
        FROM
          vertexai_books_ds.movie
      ),
      STRUCT(
        "actor_name STRING, character_name STRING, notable_quotes ARRAY<STRING>" AS output_schema,
        8192 AS max_output_tokens
      )
    );

-- 3.4.2. AI.GENERATE
SELECT
  AI.GENERATE(('Describe ', OBJ.GET_ACCESS_URL(landmarks, 'r'), ' in twenty words or less in korean'),
  connection_id => 'us-central1.gemini-conn',
  endpoint => 'gemini-2.5-flash').result
FROM vertexai_books_ds.landmarks;

-- 3.4.3. AI.GENERATE_TABLE
CREATE OR REPLACE TABLE
  `vertexai_books_ds.landmarks-metadata`
AS
  SELECT
  uri,
  image_description
FROM
AI.GENERATE_TABLE( MODEL `vertexai_books_ds.gemini-model`,
  (
  SELECT
    ('Can you describe the following image in korean?',
      OBJ.GET_ACCESS_URL(landmarks, 'r')) AS prompt,
    *
  FROM
   vertexai_books_ds.landmarks
  ),
  STRUCT ( "image_description STRING" AS output_schema ));