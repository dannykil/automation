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

ar_info = Blueprint('ar_info', __name__, url_prefix='/api/ar/info')

def connect_db():
    """PostgreSQL 데이터베이스에 연결합니다."""
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    except psycopg2.Error as e:
        print(f"데이터베이스 연결 오류: {e}")
    return conn

def insert_ar_info(conn, data):
    """ar_info 테이블에 데이터를 삽입하고 ar_info_id를 반환합니다."""
    cursor = conn.cursor()

    query = """
        INSERT INTO ar_info (job_id, transaction_date, bill_to_name, account_number, transaction_number, payment_terms, structured_payment_reference, tax_proof_type, reverse_issue_yn)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING ar_info_id;
    """

    try:
        transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date()
        cursor.execute(query, (data['job_id'], transaction_date, data['bill_to_name'], data['account_number'], data['transaction_number'], data['payment_terms'], data['structured_payment_reference'], data['tax_proof_type'], data['reverse_issue_yn']))
        ar_info_id = cursor.fetchone()[0]
        conn.commit()
        return ar_info_id
    
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ar_info 데이터 삽입 실패: {e}")
        return None
    
    finally:
        cursor.close()

def insert_ar_info_detail(conn, ar_info_id, data):
    """ar_info_detail 테이블에 데이터를 삽입합니다."""

    cursor = conn.cursor()

    query = """
        INSERT INTO ar_info_detail (ar_info_id, memo_line, description, quantity, unit_price, vat, total_amount, tax_classification, cost_center, account, project, ar_issued_yn)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    try:
        cursor.execute(query, (ar_info_id, data['memo_line'], data['description'], data['quantity'], data['unit_price'], data['vat'], data['total_amount'], data['tax_classification'], data['cost_center'], data['account'], data['project'], data['ar_issued_yn']))
        conn.commit()

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ar_info_detail 데이터 삽입 실패: {e}")

    finally:
        cursor.close()

@ar_info.route('/insert', methods=['POST'])
def insert_ar_data():
    """POST 요청으로 JSON 데이터를 받아 ar_info 및 ar_info_detail 테이블에 삽입합니다."""
    conn = connect_db()
    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    data_list = request.get_json()
    print("data_list : ", data_list)

    if not isinstance(data_list, list):
        conn.close() # 오류 발생 시 연결 닫기
        return jsonify({"error": "요청 본문은 JSON 리스트 형태여야 합니다."}), 400

    results = []

    try:
        for item in data_list:
            
            ar_info_data = item.get('ar_info')
            # print("ar_info_data : ", ar_info_data)
            ar_info_details_list = ar_info_data.get('ar_info_details') if ar_info_data else None

            if not ar_info_data or not ar_info_details_list:
                conn.close() # 오류 발생 시 연결 닫기
                return jsonify({"error": "각 아이템의 'ar_info'는 'ar_info_details' 키를 포함해야 합니다."}), 400

            ar_info_id = insert_ar_info(conn, ar_info_data)
            if ar_info_id:
                detail_insert_count = 0
                for detail_data in ar_info_details_list:
                    insert_ar_info_detail(conn, ar_info_id, detail_data)
                    detail_insert_count += 1
                results.append({"ar_info_id": ar_info_id, "inserted_details": detail_insert_count})
            else:
                results.append({"error": f"ar_info 삽입 실패: {ar_info_data.get('transaction_number') if ar_info_data else '알 수 없음'}"})

        conn.commit() # 모든 데이터 처리 후 커밋
        return jsonify({"message": "데이터 삽입 처리 완료", "results": results}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"데이터 처리 중 오류 발생: {str(e)}"}), 500

    finally:
        if conn:
            conn.close() # 마지막에 연결 닫기


def fetch_ar_info_by_job_id(conn, job_id):
    """job_id로 ar_info 테이블의 모든 데이터를 조회하고 관련 ar_info_detail 데이터를 함께 반환합니다."""
    cursor = conn.cursor()
    ar_info_query = """
        SELECT job_id, ar_info_id, transaction_date, bill_to_name, account_number,
               transaction_number, payment_terms, structured_payment_reference,
               tax_proof_type, reverse_issue_yn
        FROM ar_info
        WHERE job_id = %s;
    """
    ar_info_detail_query = """
        SELECT ar_info_detail_id, memo_line, description, quantity, unit_price,
               vat, total_amount, tax_classification, cost_center, account,
               project, ar_issued_yn
        FROM ar_info_detail
        WHERE ar_info_id = %s;
    """
    results = []
    try:
        cursor.execute(ar_info_query, (job_id,))
        ar_info_records = cursor.fetchall()

        for row in ar_info_records:
            ar_info = {
                "job_id": row[0],
                "ar_info_id": row[1],
                "transaction_date": row[2].isoformat() if row[2] else None,
                "bill_to_name": row[3],
                "account_number": row[4],
                "transaction_number": row[5],
                "payment_terms": row[6],
                "structured_payment_reference": row[7],
                "tax_proof_type": row[8],
                "reverse_issue_yn": row[9],
                "ar_info_details": []
            }
            cursor.execute(ar_info_detail_query, (ar_info["ar_info_id"],))
            ar_info_detail_records = cursor.fetchall()
            for detail_row in ar_info_detail_records:
                ar_info_detail = {
                    "ar_info_detail_id": detail_row[0],
                    "memo_line": detail_row[1],
                    "description": detail_row[2],
                    "quantity": float(detail_row[3]) if detail_row[3] else None,
                    "unit_price": float(detail_row[4]) if detail_row[4] else None,
                    "vat": float(detail_row[5]) if detail_row[5] else None,
                    "total_amount": float(detail_row[6]) if detail_row[6] else None,
                    "tax_classification": detail_row[7],
                    "cost_center": detail_row[8],
                    "account": detail_row[9],
                    "project": detail_row[10],
                    "ar_issued_yn": detail_row[11]
                }
                ar_info["ar_info_details"].append(ar_info_detail)
            results.append(ar_info)
        return results
    except psycopg2.Error as e:
        print(f"데이터 조회 실패: {e}")
        return None
    finally:
        cursor.close()

# @app.route('/api/ar_info/job/<int:job_id>', methods=['GET'])
@ar_info.route('/select/<int:job_id>', methods=['GET'])
def get_ar_info_by_job(job_id):
    """GET 요청으로 job_id를 받아 해당 job_id를 가진 모든 ar_info 데이터와 관련 ar_info_detail 데이터를 배열 형태로 반환합니다."""
    conn = connect_db()
    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    try:
        ar_info_list = fetch_ar_info_by_job_id(conn, job_id)
        if ar_info_list:
            return jsonify(ar_info_list), 200
        else:
            return jsonify({"message": f"job_id '{job_id}'에 해당하는 데이터가 없습니다."}), 404
    finally:
        if conn:
            conn.close()


def update_ar_info(conn, ar_info_id, data):
    """ar_info 테이블의 데이터를 업데이트합니다."""
    cursor = conn.cursor()
    query = """
        UPDATE ar_info
        SET job_id = %s,
            transaction_date = %s,
            bill_to_name = %s,
            account_number = %s,
            transaction_number = %s,
            payment_terms = %s,
            structured_payment_reference = %s,
            tax_proof_type = %s,
            reverse_issue_yn = %s
        WHERE ar_info_id = %s;
    """
    try:
        transaction_date = datetime.strptime(data['transaction_date'], '%Y-%m-%d').date() if data.get('transaction_date') else None
        cursor.execute(query, (data['job_id'], transaction_date, data['bill_to_name'], data['account_number'], data['transaction_number'], data['payment_terms'], data['structured_payment_reference'], data['tax_proof_type'], data['reverse_issue_yn'], ar_info_id))
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ar_info 데이터 업데이트 실패 (ar_info_id: {ar_info_id}): {e}")
        return False
    finally:
        cursor.close()

def update_ar_info_detail(conn, ar_info_detail_id, data):
    """ar_info_detail 테이블의 데이터를 업데이트합니다."""
    cursor = conn.cursor()
    query = """
        UPDATE ar_info_detail
        SET memo_line = %s,
            description = %s,
            quantity = %s,
            unit_price = %s,
            vat = %s,
            total_amount = %s,
            tax_classification = %s,
            cost_center = %s,
            account = %s,
            project = %s,
            ar_issued_yn = %s
        WHERE ar_info_detail_id = %s;
    """
    try:
        cursor.execute(query, (data['memo_line'], data['description'], data['quantity'], data['unit_price'], data['vat'], data['total_amount'], data['tax_classification'], data['cost_center'], data['account'], data['project'], data['ar_issued_yn'], ar_info_detail_id))
        conn.commit()
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ar_info_detail 데이터 업데이트 실패 (ar_info_detail_id: {ar_info_detail_id}): {e}")
        return False
    finally:
        cursor.close()

# @app.route('/api/update_ar_data', methods=['PUT'])
@ar_info.route('/update', methods=['PUT'])
def update_ar_data():
    """PUT 요청으로 JSON 데이터를 받아 ar_info 및 ar_info_detail 테이블의 데이터를 업데이트합니다."""

    conn = connect_db()

    if conn is None:
        return jsonify({"error": "데이터베이스 연결 실패"}), 500

    data_list = request.get_json()

    if not isinstance(data_list, list):
        conn.close()
        return jsonify({"error": "요청 본문은 JSON 리스트 형태여야 합니다."}), 400

    results = []

    for item in data_list:
        ar_info_data = item.get('ar_info')
        ar_info_details_list = item.get('ar_info_details')

        if not ar_info_data or 'ar_info_id' not in ar_info_data:
            results.append({"error": "각 아이템의 'ar_info'는 'ar_info_id'를 포함해야 합니다."})
            continue

        ar_info_id = ar_info_data['ar_info_id']
        ar_info_updated = update_ar_info(conn, ar_info_id, ar_info_data)
        ar_info_update_result = {"ar_info_id": ar_info_id, "updated": ar_info_updated, "details_updated": 0, "details_errors": []}

        if ar_info_details_list:
            updated_details_count = 0
            detail_errors = []

            for detail_data in ar_info_details_list:
                detail_id = detail_data.get('ar_info_detail_id')

                if detail_id:

                    if update_ar_info_detail(conn, detail_id, detail_data):
                        updated_details_count += 1

                    else:
                        detail_errors.append({"ar_info_detail_id": detail_id, "error": "업데이트 실패"})

                else:
                    detail_errors.append({"error": "ar_info_details에 'ar_info_detail_id'가 필요합니다."})

            ar_info_update_result["details_updated"] = updated_details_count
            ar_info_update_result["details_errors"] = detail_errors

        results.append(ar_info_update_result)

    conn.close()

    return jsonify({"message": "데이터 업데이트 처리 완료", "results": results}), 200