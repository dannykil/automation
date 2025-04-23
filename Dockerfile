# 베이스 이미지 선택 (원하는 파이썬 버전을 선택하세요)
FROM python:3.11-slim-buster

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일 복사
COPY requirements.txt .

# 필요한 패키지 설치
RUN pip install -r requirements.txt --no-cache-dir

# 어플리케이션 코드 복사
COPY . .

# 어플리케이션 실행 명령어 정의 (여러분의 어플리케이션 진입점을 맞춰주세요)
CMD ["python", "main.py"]