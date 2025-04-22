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

ar_job = Blueprint('ar_job', __name__, url_prefix='/api/ar/job')

def connect_db():
    """PostgreSQL 데이터베이스에 연결합니다."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

    except psycopg2.Error as e:
        print(f"데이터베이스 연결 오류: {e}")

    return conn

def insert_ar_job(conn, data):
    """ar_job 테이블에 데이터를 삽입하고 생성된 job_id를 반환합니다."""
    cursor = conn.cursor()
    query = """
        INSERT INTO ar_job (title, user_name, account, updated_at, complete_yn)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING job_id;
    """

    try:
        updated_at = datetime.strptime(data.get('updated_at'), '%Y-%m-%d %H:%M:%S') if data.get('updated_at') else None
        cursor.execute(query, (data['title'], data['user_name'], data['account'], updated_at, data['complete_yn']))
        job_id = cursor.fetchone()[0]
        conn.commit()
        return job_id
    
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ar_job 데이터 삽입 실패: {e}")
        return None
    
    finally:
        cursor.close()

@ar_job.route('/insert', methods=['POST'])
def insert_new_ar_job():
    """POST 요청으로 JSON 데이터를 받아 ar_job 테이블에 삽입합니다."""

    conn = connect_db()

    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    data = request.get_json()

    if not isinstance(data, dict):
        conn.close()
        return jsonify({"error": "요청 본문은 JSON 객체 형태여야 합니다."}), 400

    job_id = insert_ar_job(conn, data)
    conn.close()

    if job_id:
        return jsonify({"message": "ar_job 데이터 삽입 완료", "job_id": job_id}), 201
    
    else:
        return jsonify({"error": "ar_job 데이터 삽입 실패"}), 500


def fetch_all_ar_jobs(conn):
    """ar_job 테이블의 모든 데이터를 조회합니다."""

    cursor = conn.cursor()

    query = """
        SELECT job_id, title, user_name, account, created_at, updated_at, complete_yn
        FROM ar_job;
    """

    try:
        cursor.execute(query)
        records = cursor.fetchall()
        results = []

        for row in records:
            results.append({
                "job_id": row[0],
                "title": row[1],
                "user_name": row[2],
                "account": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "updated_at": row[5].isoformat() if row[5] else None,
                "complete_yn": row[6]
            })
        return results
    
    except psycopg2.Error as e:
        print(f"ar_job 데이터 조회 실패: {e}")
        return None
    
    finally:
        cursor.close()

# @app.route('/api/ar_jobs', methods=['GET'])
@ar_job.route('/select', methods=['GET'])
def get_all_ar_jobs():
    """GET 요청으로 ar_job 테이블의 모든 데이터를 리스트 형태로 반환합니다."""

    conn = connect_db()

    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    try:
        ar_jobs = fetch_all_ar_jobs(conn)

        if ar_jobs:
            return jsonify(ar_jobs), 200
        else:
            return jsonify([]), 200  # 데이터가 없으면 빈 리스트 반환
        
    finally:
        if conn:
            conn.close()

# npx create-react-app automation_frontend
# cd automation_frontend
# npm install styled-components axios