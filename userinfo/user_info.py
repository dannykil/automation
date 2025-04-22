from flask import Flask, request, jsonify, Blueprint
import psycopg2
import json

# app = Flask(__name__)
userinfo = Blueprint('userinfo', __name__, url_prefix='/api/userinfo')

# 환경 변수 또는 보안 파일에서 데이터베이스 연결 정보 로드
from common import getEnv
DB_HOST     = getEnv.get_environment_variable('DB_HOST')
DB_USER     = getEnv.get_environment_variable('DB_USER')
DB_PASSWORD = getEnv.get_environment_variable('DB_PASSWORD')
DB_NAME     = getEnv.get_environment_variable('DB_NAME')
DB_PORT     = getEnv.get_environment_variable('DB_PORT')

def connect_db():
    """PostgreSQL 데이터베이스에 연결합니다."""
    print("PostgreSQL 데이터베이스에 연결합니다.")
    
    conn = None

    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)

    except psycopg2.Error as e:
        print(f"데이터베이스 연결 오류: {e}")

    return conn

@userinfo.route('/insert', methods=['POST'])
def create_user():
    """POST 요청으로 사용자 정보를 받아 데이터베이스에 삽입합니다."""

    conn = connect_db()

    if conn is None:
        print("데이터베이스 연결 실패")
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    cur = conn.cursor()
    data = request.get_json()
    print("data : ", data)

    if not data:
        return jsonify({"error": "요청 본문에 JSON 데이터가 없습니다."}), 400

    # required_fields = ["user", "account", "password", "installed", "filepath", "filename", "reStartCount", "displayYN"]
    required_fields = ["user", "account", "password", 
                       "filepath", "filename", "reStartCount", "displayYN"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": f"필수 필드가 누락되었습니다: {', '.join(required_fields)}"}), 400

    try:
        query = """
            INSERT INTO user_info (user_name, account, password, filepath, filename, restart_count, display_yn)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at, updated_at;
        """

        values = (
            data.get("user"),
            data.get("account"),
            data.get("password"),
            # data.get("installed"),
            data.get("filepath"),
            data.get("filename"),
            int(data.get("reStartCount")),
            data.get("displayYN")
        )

        cur.execute(query, values)
        user_id, created_at, updated_at = cur.fetchone()
        conn.commit()

        return jsonify({
            "message": "사용자 정보가 성공적으로 추가되었습니다.",
            "id": user_id,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
            "data": data
        }), 201
    
    except psycopg2.Error as e:
        conn.rollback()
        return jsonify({"error": f"데이터베이스 오류: {e}"}), 500
    
    finally:
        cur.close()
        conn.close()

# if __name__ == '__main__':
#     app.run(debug=True)