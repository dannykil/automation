# prompt:
# write_log_api() 함수에서 현재 로컬에 있는 로그를 GCS로 업로드하는 기능을 추가해줘.
# 로컬 경로는 read_ndjson_log(log_date_str) 함수에서 log_file_path 참고해줘.

# prompt:
# 스케줄링으로 upload_log_api() 함수를 매시간 59분에 호출해서 GCS에 로그를 업로드 하고 있는데,
# 업로드 하기 전에 기존 로그파일을 백업하는 기능을 추가해줘.
# 백업 파일명은 YYYYMMDD.log.bak 형식으로 같은 경로에 저장해줘.
import os
from flask import Flask, request, jsonify, Blueprint
from datetime import datetime
from google.cloud import storage
import shutil

import schedule
import time
from threading import Thread

# Google Cloud Storage 설정
from common import logger, getEnv
PROJECT_ID = getEnv.get_environment_variable('PROJECT_ID')
BUCKET_NAME = getEnv.get_environment_variable('BUCKET_NAME')

log = Blueprint('log', __name__, url_prefix='/api/log')
LOG_BASE_DIR = './log'  # 로그 파일이 저장될 기본 경로

def read_ndjson_log(log_date_str):
    """주어진 날짜의 ndjson 형식 로그 파일을 읽어와 파싱된 JSON 객체 리스트를 반환합니다."""
    year = log_date_str[:4]
    month = log_date_str[4:6]
    print("year : ", year)
    print("month : ", month)
    log_file_path = os.path.join(LOG_BASE_DIR, year, month, f"{log_date_str}.log")

    log_entries = []

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    import json
                    log_entry = json.loads(line.strip())
                    log_entries.append(log_entry)
                except json.JSONDecodeError:
                    print(f"JSON 디코딩 오류: {line.strip()}")
    except FileNotFoundError:
        print(f"로그 파일 없음: {log_file_path}")
        # return None
        return log_entries
    except Exception as e:
        print(f"로그 파일 읽기 오류: {e}")
        return None

    return log_entries

@log.route('/read/<string:log_date>', methods=['GET'])
def read_log_api(log_date):
    logger.LoggerFactory._LOGGER.info("/api/log/read called")
    print("log_date : ", log_date)
    """GET 요청으로 특정 날짜의 로그 파일을 읽어와 JSON 형태로 반환합니다."""

    # log_date 형식 유효성 검사 (YYYYMMDD)
    if not (len(log_date) == 8 and log_date.isdigit()):
        return jsonify({"error": "잘못된 날짜 형식입니다. YYYYMMDD 형식으로 요청해주세요."}), 400

    log_data = read_ndjson_log(log_date)

    if log_data is not None:
        return jsonify({"message": f"{log_date} 로그 파일 읽기 성공", "data": log_data}), 200
    else:
        return jsonify({"message": f"{log_date} 로그 파일을 찾을 수 없습니다."}, 404)


def backup_log_file(log_file_path, log_date_str):
    """로그 파일을 백업합니다."""
    logger.LoggerFactory._LOGGER.info("backup_log_file(log_file_path, log_date_str) called")

    backup_filename = f"{log_date_str}.log.bak"
    backup_path = os.path.join(os.path.dirname(log_file_path), backup_filename)

    try:
        shutil.copy2(log_file_path, backup_path)  # copy2는 메타데이터도 복사
        print(f"로그 파일 {log_file_path}를 {backup_path}로 백업 완료.")
        logger.LoggerFactory._LOGGER.info(f"로그 파일 {log_file_path}를 {backup_path}로 백업 완료.")
        return True
    except Exception as e:
        print(f"로그 파일 백업 오류: {e}")
        logger.LoggerFactory._LOGGER.error(f"로그 파일 백업 오류: {e}")
        return False
    

def upload_log_to_gcs(log_file_path, year, month, log_date_str):
    """로컬 로그 파일을 Google Cloud Storage에 업로드합니다."""
    print("upload_log_to_gcs() called")
    logger.LoggerFactory._LOGGER.info("upload_log_to_gcs(log_file_path, log_date_str) called")
    logger.LoggerFactory._LOGGER.info("log_file_path : %s", log_file_path)
    logger.LoggerFactory._LOGGER.info("log_date_str  : %s", log_date_str)

    try:
        client = storage.Client(project=PROJECT_ID)
        bucket = client.get_bucket(BUCKET_NAME)
        # blob = bucket.blob(f"logs/{log_date_str}.log")  # GCS에 저장될 경로 및 파일명
        blob = bucket.blob(f"logs/{year}/{month}/{log_date_str}.log")  # GCS에 저장될 경로 및 파일명
        
        blob.upload_from_filename(log_file_path)
        print(f"로그 파일 {log_file_path}를 GCS 버킷 {BUCKET_NAME}에 업로드 완료.")
        return True
    except Exception as e:
        print(f"GCS 업로드 오류: {e}")
        return False
    

@log.route('/upload', methods=['GET'])
def upload_log_api():
    print("/api/log/upload called")
    logger.LoggerFactory._LOGGER.info("/api/log/upload called")

    # 현재 날짜를 YYYYMMDD 형식으로 생성
    now = datetime.now()
    log_date_str = now.strftime("%Y%m%d")

    # 로그 파일 경로 가져오기
    year = log_date_str[:4]
    month = log_date_str[4:6]
    log_file_path = os.path.join(LOG_BASE_DIR, year, month, f"{log_date_str}.log")

    # # GCS로 로그 파일 업로드
    # if upload_log_to_gcs(log_file_path, year, month, log_date_str):
    #     return jsonify({"message": f"{log_date_str} 로그 파일 GCS 업로드 요청 성공"}), 200
    # else:
    #     return jsonify({"error": f"{log_date_str} 로그 파일 GCS 업로드 실패"}), 500
    
    # 백업 먼저 수행
    if backup_log_file(log_file_path, log_date_str):
        # GCS로 로그 파일 업로드
        if upload_log_to_gcs(log_file_path, year, month, log_date_str):
            return jsonify({"message": f"{log_date_str} 로그 파일 백업 및 GCS 업로드 요청 성공"}), 200
        else:
            return jsonify({"error": f"{log_date_str} 로그 파일 GCS 업로드 실패"}), 500
    else:
        return jsonify({"error": f"{log_date_str} 로그 파일 백업 실패"}), 500


# def run_scheduler(app):
#     with app.app_context():
#         schedule.every().hour.at(":59").do(upload_log_api)
#         while True:
#             schedule.run_pending()
#             time.sleep(1)


# def start_scheduler(app):
#     scheduler_thread = Thread(target=run_scheduler, args=(app,)) # app 객체를 인자로 전달
#     scheduler_thread.daemon = True
#     scheduler_thread.start()
