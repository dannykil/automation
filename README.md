# 사용법

# 특이사항

# 개발 시 XPATH를 설정하는 방법 4가지

# 1)

# Exception 정리

- 가상환경 사용법

1. 가상환경 조회
   conda info --envs
   conda env list

2. 가상환경 생성
   conda create -n 8page python=3.12

3. 가상환경 활성화
   conda activate 8page

4. 가상환경 비활성화
   conda deactivate

5. 가상환경 삭제
   conda remove -n 8page --all

6. 가상환경 내 패키지 설치
   conda install <패키지명>
   pip install -r requirements.txt

7. 가상환경 내 설치된 패키지 추출
   pip freeze > requirements.txt

2) 현재 사용중인 프로젝트
   gcloud config get project

   gcloud auth login
   gcloud auth application-default login
   Credentials saved to file: [/Users/danniel.kil/.config/gcloud/application_default_credentials.json]
   These credentials will be used by any library that requests Application Default Credentials (ADC).
   gcloud config set account danniel.kil@gmail.com
   gcloud config set project PROJECT_ID

3) 프로젝트 변경
   gcloud config set project PROJECT_ID
   gcloud config set project gen-lang-client-0274842719
   gcloud config set project quintet-hist-poc
   gcloud auth application-default set-quota-project gen-lang-client-0274842719
   gcloud auth application-default set-quota-project quintet-hist-poc
   - 권한이 없는 경우 아래와 같은 메시지 발생
     Are you sure you wish to set property [core/project] to gen-lang-client-0480088393?
     Do you want to continue (Y/n)? Y
4) quota project 할당안됨

- 에러코드 : UserWarning: Your application has authenticated using end user credentials from Google Cloud SDK without a quota project. You might receive a "quota exceeded" or "API not enabled" error. See the following page for troubleshooting: https://cloud.google.com/docs/authentication/adc-troubleshooting/user-creds
- 해결방법 : gcloud auth application-default set-quota-project YOUR_PROJECT

-- danniel.kil@gmail.com
gcloud auth application-default login
gcloud auth application-default set-quota-project gen-lang-client-0274842719

-- jm.kil@hist.co.kr
gcloud auth application-default login
gcloud auth application-default set-quota-project quintet-hist-poc
