# prompt:
# 이렇게해 실행하면 오류가 나는데 어느 부분이 잘못된거야?
FROM python:3.11-slim-buster

# 환경 변수 설정 (기본: dev)
ENV ENV=dev

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일 복사
COPY requirements.txt .
# COPY .env.dev /app/.env.dev
COPY .env.dev .

# 필요한 패키지 설치
RUN pip install -r requirements.txt --no-cache-dir

# 어플리케이션 코드 복사
COPY . .

# 어플리케이션 실행 명령어 정의 (여러분의 어플리케이션 진입점을 맞춰주세요)
CMD ["python", "main.py"]

# gcloud builds triggers update automation-dev --logging=CLOUD_LOGGING_ONLY

# 
# docker build -t automation_backend .
# docker run -d -p 5000:5000 automation_backend
# docker run -e ENV=dev -d -p 5000:5000 automation_backend
# docker run -v ~/.config/gcloud:/root/.config/gcloud -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json -p 8000:8000 <이미지_이름>
# /Users/danniel.kil/.config/gcloud/application_default_credentials.json
# docker run -e GOOGLE_APPLICATION_CREDENTIALS=/Users/danniel.kil/.config/gcloud/application_default_credentials.json -d -p 5000:5000 automation_backend
# docker exec -it a3e541cd552b /bin/sh

# ENV=dev python main.py

# prompt:
# 도커 컨테이너로 올린 파이썬 백엔드 어플리케이션을 실행하면 아래와 같은 에러메시지가 발생하고 있어.
# .env.dev 파일도 정상적으로 읽고 있는 것 같은데, 왜 에러가 나는거지?
# File "/usr/local/lib/python3.11/site-packages/google/auth/_default.py", line 685, in default
# raise exceptions.DefaultCredentialsError(_CLOUD_SDK_MISSING_CREDENTIALS)
# google.auth.exceptions.DefaultCredentialsError: Your default credentials were not found. To set up Application Default Credentials, see https://cloud.google.com/docs/authentication/external/set-up-adc for more information.