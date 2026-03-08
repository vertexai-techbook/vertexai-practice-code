# == 2. 파일 검색 스토어 만들기 == #
import os
from google import genai

# 클라이언트 초기화
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# File Search Store 생성
file_search_store = client.file_search_stores.create(config={'display_name': '기사 본문 저장소'})
print(file_search_store.name)

# == 3. 파일 업로드 == #
import time

file_search_store_name = 'fileSearchStores/<저장소ID>'

operation = client.file_search_stores.upload_to_file_search_store(
    file='article.json',
    file_search_store_name=file_search_store_name,
    config={'display_name': '기사 본문'}
)

while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

print("파일 업로드 및 인덱싱 완료")

# == 4. 검색 및 답변 == #
from google.genai import types

query = "전기차 주행거리가 얼마나 돼?"

# File Search 도구를 포함하여 질문
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=query,
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store_name]
                )
            )
        ]
    )
)
print(response.text)

# == 5. 답변 근거 확인(Grounding Metadata) == #
grounding_metadata = response.candidates[0].grounding_metadata

# 답변의 어느 부분이 몇 번째 청크를 참고했는지 확인
for support in grounding_metadata.grounding_supports:
    print(f"생성된 문장: {support.segment.text}")
    print(f"참고한 자료 인덱스: [{support.grounding_chunk_indices}]")
    print("-" * 20)

if grounding_metadata.grounding_chunks:
    references = [
        chunk.retrieved_context.text
        for chunk in grounding_metadata.grounding_chunks
    ]

    # 참고 자료 묶음 출력
    for i, text in enumerate(references):
        print(f"[참고 자료 인덱스 {i}]")
        print(text)
        print("\n")
else:
    print("참고한 기사가 없습니다.")

# == 6. 메타데이터 필터링 == #
# 커스텀 메타데이터 지정
operation = client.file_search_stores.import_file(
    file_search_store_name=file_search_store.name,
    file_name=sample_file.name,
    custom_metadata=[
        {"key": "reporter", "string_value": "홍길동"},
        {"key": "id", "numeric_value": 60}
    ]
)

# 필터링 구현
file_search=types.FileSearch(
    file_search_store_names=[file_search_store.name],
    metadata_filter="id=60",
)

# == 7. 스토어 관리 == #
# 현재 생성된 모든 저장소 목록 조회
print("저장소 목록")
for store in client.file_search_stores.list():
    print(f"이름: {store.display_name}, ID: {store.name}")

# 특정 저장소의 상세 정보 확인
print("\n저장소 상세 정보")
search_store = client.file_search_stores.get(name=store.name)
print(search_store)

# 저장소 삭제
# 저장소를 삭제하면 내부의 인덱싱된 데이터도 모두 사라집니다.
client.file_search_stores.delete(name=store.name, config={'force': True}) # force=True: 안에 파일이 있어도 강제로 삭제
print("\n삭제 완료")