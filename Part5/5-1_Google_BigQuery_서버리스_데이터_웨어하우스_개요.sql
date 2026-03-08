-- 3.1. 기본 조회 쿼리 (SELECT)
SELECT
  id,
  title,
  view_count,
  creation_date
FROM
  `bigquery-public-data.stackoverflow.posts_questions`
WHERE
  tags LIKE '%python%'
ORDER BY
  view_count DESC
LIMIT 10;

-- 3.2. 집계 및 분석 쿼리 (GROUP BY)
SELECT
  EXTRACT(YEAR FROM creation_date) AS year,
  COUNT(*) AS post_count
FROM
  `bigquery-public-data.stackoverflow.posts_questions`
WHERE
  tags LIKE '%python%'
GROUP BY
  year
ORDER BY
  year DESC;

-- 3.3. 조인 쿼리 (JOIN)
SELECT
  q.id,
  q.title,
  q.view_count,
  COUNT(a.id) AS answer_count
FROM
  `bigquery-public-data.stackoverflow.posts_questions` AS q
LEFT JOIN
  `bigquery-public-data.stackoverflow.posts_answers` AS a
ON
  q.id = a.parent_id
WHERE
  q.tags LIKE '%python%'
GROUP BY
  q.id, q.title, q.view_count
ORDER BY
  answer_count DESC
LIMIT 10;

-- 3.4. 윈도우 함수
SELECT
  *
FROM (
  SELECT
    id,
    title,
    view_count,
    EXTRACT(YEAR FROM creation_date) AS year,
    ROW_NUMBER() OVER (
      PARTITION BY EXTRACT(YEAR FROM creation_date)
      ORDER BY view_count DESC
    ) AS rank
  FROM
    `bigquery-public-data.stackoverflow.posts_questions`
  WHERE
    tags LIKE '%python%'
)
WHERE
  rank <= 3
ORDER BY
  year DESC, rank;

-- 3.5. 서브쿼리와 CTE (Common Table Expressions)
WITH python_questions AS (
  SELECT
    id,
    title,
    view_count,
    answer_count,
    creation_date
  FROM
    `bigquery-public-data.stackoverflow.posts_questions`
  WHERE
    tags LIKE '%python%'
    AND answer_count > 0
),
avg_stats AS (
  SELECT
    AVG(view_count) AS avg_views,
    AVG(answer_count) AS avg_answers
  FROM
    python_questions
)
SELECT
  pq.title,
  pq.view_count,
  pq.answer_count,
  ROUND(pq.view_count / ast.avg_views, 2) AS view_ratio,
  ROUND(pq.answer_count / ast.avg_answers, 2) AS answer_ratio
FROM
  python_questions AS pq
CROSS JOIN
  avg_stats AS ast
WHERE
  pq.view_count > ast.avg_views
ORDER BY
  view_ratio DESC
LIMIT 20;

-- 3.6. 배열과 구조체 다루기
SELECT
  id,
  title,
  tag
FROM
  `bigquery-public-data.stackoverflow.posts_questions`,
  UNNEST(SPLIT(tags, '|')) AS tag
WHERE
  tag = 'python'
LIMIT 10;