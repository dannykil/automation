import psycopg2
from flask import Flask, request, jsonify, Blueprint
from datetime import datetime

# app = Flask(__name__)

# 환경 변수 또는 보안 파일에서 데이터베이스 연결 정보 로드
from common import getEnv
DB_HOST     = getEnv.get_environment_variable('DB_HOST')
DB_USER     = getEnv.get_environment_variable('DB_USER')
DB_PASSWORD = getEnv.get_environment_variable('DB_PASSWORD')
DB_NAME     = getEnv.get_environment_variable('DB_NAME')
DB_PORT     = getEnv.get_environment_variable('DB_PORT')

userinfo = Blueprint('userinfo', __name__, url_prefix='/api/userinfo')

def connect_db():
    """데이터베이스에 연결합니다."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        return conn
    except psycopg2.Error as e:
        print(f"데이터베이스 연결 실패: {e}")
        return None

def insert_user_info(conn, data):
    """제공된 JSON 데이터를 기반으로 PostgreSQL 데이터베이스에 사용자 정보를 삽입합니다."""
    cursor = conn.cursor()
    query = """
        INSERT INTO user_info (user_name, account, password, restart_count, display_yn, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING account;
    """

    try:
        user_name = data.get('user')
        account = data.get('account')
        password = data.get('password')
        restart_count = int(data.get('reStartCount', 0))
        display_yn = data.get('displayYN', 'N')
        created_at = datetime.now()

        cursor.execute(query, (user_name, account, password, restart_count, display_yn, created_at))
        conn.commit()
        return account

    except psycopg2.Error as e:
        conn.rollback()
        print(f"사용자 정보 삽입 실패: {e}")
        return None

    finally:
        cursor.close()

@userinfo.route('/insert', methods=['POST'])
def insert_new_user_info():
    """POST 요청으로 JSON 데이터를 받아 사용자 정보를 테이블에 삽입합니다."""

    conn = connect_db()

    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    data = request.get_json()

    if not isinstance(data, dict):
        conn.close()
        return jsonify({"error": "요청 본문은 JSON 객체 형태여야 합니다."}), 400

    account = insert_user_info(conn, data)
    conn.close()

    if account:
        return jsonify({"message": "사용자 정보 삽입 완료", "account": account}), 201
    else:
        return jsonify({"error": "사용자 정보 삽입 실패"}), 500

# if __name__ == '__main__':
#     app.run(debug=True)