import os
from flask import Flask, request, jsonify, Blueprint
from datetime import datetime

log = Blueprint('log', __name__, url_prefix='/api/log')
LOG_BASE_DIR = './log'  # 로그 파일이 저장될 기본 경로

def read_ndjson_log(log_date_str):
    """주어진 날짜의 ndjson 형식 로그 파일을 읽어와 파싱된 JSON 객체 리스트를 반환합니다."""
    year = log_date_str[:4]
    month = log_date_str[4:6]
    print("year : ", year)
    print("month : ", month)
    log_file_path = os.path.join(LOG_BASE_DIR, year, month, f"{log_date_str}.log")
    print("1")

    log_entries = []
    try:
        print("2")
        with open(log_file_path, 'r', encoding='utf-8') as f:
            print("3")
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

# if __name__ == '__main__':
#     app = Flask(__name__)
#     app.register_blueprint(log_bp)
#     app.run(debug=True)