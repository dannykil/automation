from flask import Flask, request, jsonify, Blueprint
import psycopg2
from datetime import datetime

app = Flask(__name__)

# 환경 변수 또는 보안 파일에서 데이터베이스 연결 정보 로드
from common import getEnv
DB_HOST     = getEnv.get_environment_variable('DB_HOST')
DB_USER     = getEnv.get_environment_variable('DB_USER')
DB_PASSWORD = getEnv.get_environment_variable('DB_PASSWORD')
DB_NAME     = getEnv.get_environment_variable('DB_NAME')
DB_PORT     = getEnv.get_environment_variable('DB_PORT')

ar_event = Blueprint('ar_event', __name__, url_prefix='/api/ar/event')

def connect_db():
    """PostgreSQL 데이터베이스에 연결합니다."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

    except psycopg2.Error as e:
        print(f"데이터베이스 연결 오류: {e}")

    return conn

def insert_ar_event(conn, data):
    """ar_event 테이블에 데이터를 삽입하고 생성된 event_id를 반환합니다."""
    cursor = conn.cursor()
    query = """
        INSERT INTO ar_event (process, mapped_xpath_id, xpath, description, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING event_id;
    """

    try:
        created_at = datetime.now()
        cursor.execute(query, (data.get('process'), data.get('mapped_xpath_id'), data.get('xpath'), data.get('description'), created_at))
        event_id = cursor.fetchone()[0]
        conn.commit()
        return event_id

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ar_event 데이터 삽입 실패: {e}")
        return None

    finally:
        cursor.close()

@ar_event.route('/insert', methods=['POST'])
def insert_new_ar_event():
    """POST 요청으로 JSON 데이터를 받아 ar_event 테이블에 삽입합니다."""

    conn = connect_db()

    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    data = request.get_json()

    if not isinstance(data, dict):
        conn.close()
        return jsonify({"error": "요청 본문은 JSON 객체 형태여야 합니다."}), 400

    event_id = insert_ar_event(conn, data)
    conn.close()

    if event_id:
        return jsonify({"message": "ar_event 데이터 삽입 완료", "event_id": event_id}), 201
    else:
        return jsonify({"error": "ar_event 데이터 삽입 실패"}), 500

# npx create-react-app automation_frontend
# cd automation_frontend
# npm install styled-components axios