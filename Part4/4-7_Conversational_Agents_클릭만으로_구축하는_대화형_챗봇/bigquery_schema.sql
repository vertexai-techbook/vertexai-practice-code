CREATE TABLE `vertexai-books.vertexai_books_ds.conversation_history`
(
  project_id STRING,
  agent_id STRING,
  conversation_name STRING,
  turn_position INT64,
  request_time TIMESTAMP,
  language_code STRING,
  request JSON,
  response JSON,
  partial_responses JSON,
  derived_data JSON,
  conversation_signals JSON,
  bot_answer_feedback JSON
);