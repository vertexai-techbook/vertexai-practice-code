# 1. 파이썬 베이스 이미지
FROM python:3.12-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필수 패키지 설치를 위한 requirements.txt 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 복사 (현재 폴더의 모든 파일을 컨테이너로 복사)
COPY . .

# 5. 실행 권한 부여
RUN chmod +x main.py mcp_server.py

# 6. Cloud Run에서 제공하는 PORT 환경변수 사용
ENV PORT=8080

# 7. 컨테이너 시작 시 실행할 명령어
# MCP 서버를 백그라운드로 띄우고, 5초 대기 후 에이전트 실행
CMD python mcp_server.py & sleep 5 && python agent.py