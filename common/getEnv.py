# prompt:
# 아래 소스코드에 환경에 따라 .env.dev 또는 .env.prd로 구분되는데 Dockerfile에서 실행할 때 명시되는 부분이 없어서 그런걸까?
from dotenv import load_dotenv
import os
import sys

# getEnv.py 파일이 있는 경로를 sys.path에 추가
common_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(common_dir)
import getEnv
# print("common_dir : ", common_dir)

def load_environment_variables(env_file):
    """환경 변수 파일을 로드합니다."""
    load_dotenv(dotenv_path=env_file)

def get_environment_variable(key):
    """환경 변수 값을 가져옵니다."""
    return os.getenv(key)

# 환경 변수 로드 (빌드 시 환경에 따라 파일 선택)
print("ENV : ", os.environ.get('ENV'))
if os.environ.get('ENV') == 'prd':
    load_environment_variables('.env.prd')
else:
    load_environment_variables('.env.dev')