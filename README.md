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
