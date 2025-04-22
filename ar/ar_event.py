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
    """데이터베이스에 연결합니다."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        return conn
    except psycopg2.Error as e:
        print(f"데이터베이스 연결 실패: {e}")
        return None

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
    """POST 요청으로 JSON 데이터를 받아 ar_event 테이블에 삽입합니다 (복수 데이터 처리)."""

    conn = connect_db()

    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    data_list = request.get_json()

    if not isinstance(data_list, list):
        conn.close()
        return jsonify({"error": "요청 본문은 JSON 리스트 형태여야 합니다."}), 400

    inserted_ids = []
    for data in data_list:
        if isinstance(data, dict):
            event_id = insert_ar_event(conn, data)
            if event_id:
                inserted_ids.append(event_id)
            else:
                conn.close()
                return jsonify({"error": f"데이터 삽입 실패: {data}"}), 500
        else:
            conn.close()
            return jsonify({"error": "요청 본문 내 각 요소는 JSON 객체 형태여야 합니다."}), 400

    conn.close()
    return jsonify({"message": f"{len(inserted_ids)}개의 ar_event 데이터 삽입 완료", "event_ids": inserted_ids}), 201


def fetch_ar_events(conn, event_id=None, process=None, mapped_xpath_id=None):
    """ar_event 테이블의 데이터를 조회합니다. 조건이 주어지면 해당 조건에 맞는 데이터만 반환합니다."""
    cursor = conn.cursor()
    query = "SELECT event_id, process, mapped_xpath_id, xpath, description, created_at, updated_at FROM ar_event"
    conditions = []
    params = []

    if event_id is not None:
        conditions.append("event_id = %s")
        params.append(event_id)
    if process is not None:
        conditions.append("process = %s")
        params.append(process)
    if mapped_xpath_id is not None:
        conditions.append("mapped_xpath_id = %s")
        params.append(mapped_xpath_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    try:
        cursor.execute(query, tuple(params))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    except psycopg2.Error as e:
        print(f"ar_event 데이터 조회 실패: {e}")
        return None
    finally:
        cursor.close()

@ar_event.route('/select', methods=['GET'])
def get_ar_events():
    """GET 요청으로 ar_event 테이블의 데이터를 조회합니다. 쿼리 파라미터를 사용하여 필터링할 수 있습니다."""
    conn = connect_db()

    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    event_id = request.args.get('event_id')
    process = request.args.get('process')
    mapped_xpath_id = request.args.get('mapped_xpath_id')

    events = fetch_ar_events(conn, event_id=event_id, process=process, mapped_xpath_id=mapped_xpath_id)
    conn.close()

    if events is not None:
        return jsonify(events), 200
    else:
        return jsonify({"error": "ar_event 데이터 조회 실패"}), 500