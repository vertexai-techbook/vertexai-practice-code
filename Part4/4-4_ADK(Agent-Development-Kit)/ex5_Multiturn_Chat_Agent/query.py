import asyncio
from vertexai import agent_engines

async def main():
    app = agent_engines.get("<배포된 에이전트 리소스 이름>")
    user_id = "remote_user_123"

    session = await app.async_create_session(user_id=user_id)
    session_id = session["id"]
    print(f"챗봇이 시작되었습니다. (세션 ID: {session_id}, 사용자 ID: {user_id})")
    print("대화를 종료하려면 'exit'를 입력하세요.")

    # 3단계: 사용자와의 실시간 대화 루프
    while True:
        user_query = await asyncio.to_thread(input, "사용자👨‍💻 > ")
        if user_query.lower() == 'exit':
            print("챗봇을 종료합니다.")
            break

        # 종료 명령어 확인
        if user_query.lower() == "exit":
            print("챗봇을 종료합니다. 안녕히 가세요!")
            break

        # 4단계: 쿼리 전송 및 응답 스트리밍
        events = []

        # 동일한 세션 ID를 계속 재사용하여 대화의 맥락을 유지
        async for event in app.async_stream_query(
            user_id=user_id,
            session_id=session_id,
            message=user_query
        ):
            events.append(event)
           
        final_text_responses = [
            e for e in events
            if e.get("content", {}).get("parts", [{}])[0].get("text")
            and not e.get("content", {}).get("parts", [{}])[0].get("function_call")
        ]
        if final_text_responses:
            response = final_text_responses[0]["content"]["parts"][0]["text"]
            print(f"챗봇✨ > {response}")

# 스크립트 실행
if __name__ == "__main__":
    asyncio.run(main())