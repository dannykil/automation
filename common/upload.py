# prompt:
# 이 부분이 파일 업로드 시 호출되는 백엔드 소스코드인데 여기에서 수정할 부분이 있어?

# prompt:
# boards와 files 테이블에서 데이터를 가져오는 api를 개발하고 싶은데 아래 소스코드를 참고해서 작성해줘.
from flask import Flask, request, jsonify, Blueprint
from google.cloud import storage
import os
import psycopg2
from datetime import datetime

uploader = Blueprint('uploader', __name__, url_prefix='/api/file')

# Google Cloud Storage 설정
from common import logger, getEnv
PROJECT_ID = getEnv.get_environment_variable('PROJECT_ID')
BUCKET_NAME = getEnv.get_environment_variable('BUCKET_NAME')
print("PROJECT_ID  : ", PROJECT_ID)
print("BUCKET_NAME : ", BUCKET_NAME)

if not PROJECT_ID or not BUCKET_NAME:
    raise ValueError("GCP_PROJECT_ID and GCP_BUCKET_NAME environment variables must be set.")

storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)

# PostgreSQL 연결 설정
DB_HOST = getEnv.get_environment_variable('DB_HOST')
DB_NAME = getEnv.get_environment_variable('DB_NAME')
DB_USER = getEnv.get_environment_variable('DB_USER')
DB_PASSWORD = getEnv.get_environment_variable('DB_PASSWORD')

def get_db_connection():
    logger.LoggerFactory._LOGGER.info("get_db_connection() called")
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    return conn

# prompt: 
# 아래 소스코드는 게시물을 등록하면서 파일도 같이 업로드하는데 이 때 파일 정보들도 같이 DBㅇ에 저장하는 소스코드야.
# 근데 다른건 다 이상없는데 filesize(file.content_length)이 계속 0으로 저장되고 있어. 
# 혹시 이유를 알 수 있어?

# prompt:
# 이게 이전에 사용하던 DB Insert 소스코드야. 이걸 참조해서 다시 작성해줘.
@uploader.route('/upload', methods=['POST'])
def upload_file():
    print("upload_file() called")
    logger.LoggerFactory._LOGGER.info("upload_file() called")

    if 'title' not in request.form:
        return jsonify({'error': 'Title is required'}), 400

    title = request.form['title']
    files = request.files.getlist('files')

    if not files or len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400

    filenames = []

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        now = datetime.now()

        # boards 테이블에 정보 저장
        sql_boards = "INSERT INTO boards (title, created_at, updated_at) VALUES (%s, %s, %s) RETURNING id;"
        cur.execute(sql_boards, (title, now, now))
        board_id = cur.fetchone()[0]

        for file in files:
            if file.filename == '':
                continue

            blob = bucket.blob(file.filename)
            blob.upload_from_file(file)

            gcs_path = f"gs://{BUCKET_NAME}/{file.filename}"

            filenames.append(file.filename)

            # GCS에 업로드된 Blob 객체의 크기 확인
            blob.reload()  # 최신 메타데이터 로드
            file_size_gcs = blob.size

            # files 테이블에 각 파일 정보 저장
            sql_files = "INSERT INTO files (board_id, filename, filetype, filepath, filesize) VALUES (%s, %s, %s, %s, %s);"
            print(sql_files)

            cur.execute(sql_files, (board_id, file.filename, file.content_type, gcs_path, file_size_gcs))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'redirectUrl': '/board', 'filenames': filenames}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f'Failed to upload and save: {str(e)}'}), 500

    finally:
        if conn:
            conn.close()


@uploader.route('/boards', methods=['GET'])
def get_boards_with_files():
    print("get_boards_with_files() called")
    logger.LoggerFactory._LOGGER.info("get_boards_with_files() called")

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # boards 테이블의 모든 데이터 조회
        cur.execute("SELECT id, title, created_at, updated_at FROM boards ORDER BY created_at DESC;")
        boards_data = cur.fetchall()
        boards = []
        for row in boards_data:
            board = {
                'id': row[0],
                'title': row[1],
                'created_at': row[2].isoformat(),
                'updated_at': row[3].isoformat()
            }
            boards.append(board)

        # 각 board_id에 해당하는 files 테이블 데이터 조회
        for board in boards:
            board_id = board['id']
            cur.execute("SELECT id, board_id, filename, filetype, filepath, filesize, analysis_yn FROM files WHERE board_id = %s;", (board_id,))
            files_data = cur.fetchall()
            files = []
            for file_row in files_data:
                file = {
                    'id': file_row[0],
                    'board_id': file_row[1],
                    'filename': file_row[2],
                    'filetype': file_row[3],
                    'filepath': file_row[4],
                    'filesize': file_row[5],
                    'analysis_yn': file_row[6]
                }
                files.append(file)
            board['files'] = files

            # 각 board_id에 해당하는 purchase_order 테이블 데이터 조회
            select_sql = """
                SELECT id, board_id, file_id, filepath, created_at, ordering_company, ordering_manager, order_date, order_item, order_quantity, order_amount, order_number, delivery_company, delivery_deadline, customer_manager
                FROM purchase_order WHERE board_id = %s;
            """
            cur.execute(select_sql, (board_id,))
            analysis_data = cur.fetchall()
            analysiss = []
            for analysis_row in analysis_data:
                analysis = {
                    'id': analysis_row[0],
                    'board_id': analysis_row[1],
                    'file_id': analysis_row[2],
                    'ordering_company': analysis_row[5],
                    'order_date': analysis_row[7],
                    'order_item': analysis_row[8],
                    'order_quantity': analysis_row[9],
                    'order_amount': analysis_row[10]
                }
                analysiss.append(analysis)
            board['analysis'] = analysiss
    
        cur.close()
        return jsonify(boards), 200

    except Exception as e:
        print(f"Error fetching boards and files: {e}")
        logger.LoggerFactory._LOGGER.info(f"Error fetching boards and files: {e}")
        return jsonify({'error': f'Failed to fetch boards and files: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()