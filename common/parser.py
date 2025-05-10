# prompt:
# 파이썬으로 프론트에서 전달한 파라미터(id, board_id, filename)를 확인하는 api를 개발해줘.

# prompt: 
# 너 말대로 로그를 보니까 아래와 같이 리다이렉트(HTTP 상태 코드 3xx)를 포함하고 있어.
# {"timestamp": "2025-05-06 10:09:19,269", "level": "INFO", "filename": "_internal.py", "function": "_log", "lineno": 97, "message": "127.0.0.1 - - [06/May/2025 10:09:19] \"\u001b[32mOPTIONS /api/parser HTTP/1.1\u001b[0m\" 308 -"}
# 근데 소스코드에는 리다이렉트가 없는데 왜 리다이렉트가 발생하는거지?

# prompt: 
# 자, 이제 내가 만든 기능을 합쳐 완성시켜보려고 해. 목표와 Instruction을 참고해서 작업 진행해줘.
# 목표 : 파일 분석 및 추출 후 진행 과정에 생성된 데이터(txt, json 등)들을 모두 백업하고 추출된 결과를 Cloud SQL Postgre DB에 Insert 및 화면에 보여주기.
# 1) 현재 개발한 3개의 함수 process_document_sample(), analysis_document_sample(), read_file_from_gcs()을 하나의 함수로 합치기.
# 2) read_file_from_gcs()에서 GCS에 업로드가 완료되면 DB customer table에 Insert하는 기능을 추가하기.
# 3) 정상적으로 DB customer table에 Insert되면 DB files 테이블의 상태값(analysis_yn)을 'Y'로 업데이트하는 기능을 추가하기.
# 4) 이 모든 작업이 끝나면 최종적으로 DB에 Insert된 데이터를 json으로 변환해서 response로 전달하기.
# 5) 프론트엔드 BoardListWithFiles 컴포넌트에 CustomerListWithFiles 컴포넌트를 추가해서 DB에 Insert된 데이터를 화면에 보여주기.
# 먼저 백엔드부터 수정해보려고 해. 아래 소스코드를 참고해서 수정해줘.
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
from google.cloud import storage
import os
from google.cloud import aiplatform
from google import genai
import json
from datetime import datetime
# from google.genai.types import HttpOptions


from flask import Blueprint, request, jsonify
parser = Blueprint('parser', __name__, url_prefix='/api/parser')

from common import getEnv
PROJECT_ID    = getEnv.get_environment_variable('PROJECT_ID')
LOCATION      = getEnv.get_environment_variable('LOCATION')
PROCESSOR_ID  = getEnv.get_environment_variable('PROCESSOR_ID')
BUCKET_NAME   = getEnv.get_environment_variable('BUCKET_NAME')
GCS_FILE_PATH = getEnv.get_environment_variable('GCS_FILE_PATH')
GCS_FILE_PATH_ORIGIN = getEnv.get_environment_variable('GCS_FILE_PATH_ORIGIN')
GCS_FILE_PATH_PARSED = getEnv.get_environment_variable('GCS_FILE_PATH_PARSED')
GCS_FILE_PATH_JSON   = getEnv.get_environment_variable('GCS_FILE_PATH_JSON')

# PostgreSQL 연결 설정
import psycopg2  # PostgreSQL 라이브러리
DB_HOST = getEnv.get_environment_variable('DB_HOST')
DB_PORT = getEnv.get_environment_variable('DB_PORT')
DB_NAME = getEnv.get_environment_variable('DB_NAME')
DB_USER = getEnv.get_environment_variable('DB_USER')
DB_PASSWORD = getEnv.get_environment_variable('DB_PASSWORD')

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    return conn

# TODO(developer): Uncomment these variables before running the sample.
project_id   = PROJECT_ID
location     = "us" # Format is "us" or "eu"
processor_id = PROCESSOR_ID
# file_path    = GCS_FILE_PATH
mime_type    = "application/pdf" # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
field_mask = "text,entities,pages.pageNumber"  # Optional. The fields to return in the Document object.
processor_version_id = "pretrained-form-parser-v2.1-2023-06-26" # Optional. Processor version to use
gcs_bucket_name = BUCKET_NAME
gcs_file_path = "documents_parsed/parsed_document.txt"  # GCS에 저장될 파일 경로 (버킷 이름 제외)
gcs_file_path_json = "documents_json/document.json"  

# @parser.route('/test2', methods=['POST'])
# def process_document_sample2():
#     print("process_document_sample() called")

#     data = request.get_json()
#     print(f"Received data: {data}")

#     if not data:
#         return jsonify({'error': 'No JSON data received'}), 400

#     file_id = data.get('id')
#     board_id = data.get('board_id')
#     filename = data.get('filename')
#     filepath = data.get('filepath')

#     print(f"Received file ID: {file_id}")
#     print(f"Received board ID: {board_id}")
#     print(f"Received filename: {filename}")
#     print(f"Received filepath: {filepath}")

#     # orders 테이블에 직접 삽입
#     conn = get_db_connection()
#     cur = conn.cursor()

#     # 삽입된 데이터 조회 (board_id 사용)

#     # prompt:
#     # purchase_order에서 board_id를 기준으로 Select해서 리액트로 개발된 프론트엔드에 전달할 수 있도록 json으로 변환해서 response로 전달해줘.
#     select_sql = """
#         SELECT id, board_id, file_id, filepath, created_at, ordering_company, ordering_manager, order_date, order_item, order_quantity, order_amount, order_number, delivery_company, delivery_deadline, customer_manager
#         FROM purchase_order
#         WHERE board_id = %s;
#     """
#     cur.execute(select_sql, (board_id,))
#     result = cur.fetchall()
#     print("result : ", result)

#     if result:
#         # 컬럼명과 값을 매핑하는 딕셔너리 생성
#         columns = [column[0] for column in cur.description]
#         order_data_from_db = dict(zip(columns, result))

#         # analysiss = []
#         # for analysis in result:
#         #     analysis = {
#         #         'ordering_company': analysis[5],
#         #         'order_date': analysis[7],
#         #         'order_item': analysis[8],
#         #         'order_quantity': analysis[9],
#         #         'order_amount': analysis[10]
#         #     }
#         #     analysiss.append(analysis)
#         # analysis['analysis'] = analysiss
#         # files_data = cur.fetchall()
#         analysis = {}
#         analysiss = []
#         for analysis_row in result:
#             analysis = {
#                 'ordering_company': analysis_row[5],
#                 'order_date': analysis_row[7],
#                 'order_item': analysis_row[8],
#                 'order_quantity': analysis_row[9],
#                 'order_amount': analysis_row[10]
#             }
#             analysiss.append(analysis)
#         # analysis['analysis'] = analysiss
#         # print(analysis['analysis'])
#         print("analysiss : ", analysiss)

#         cur.close()
#         conn.close()

#         return jsonify(analysiss), 200 # Return the result
#         # return jsonify(analysiss), 200 # Return the result

#     else:
#         return jsonify({'error': 'Failed to retrieve order data after insertion'}), 500


# prompt:
# 파일 분석이 끝나면 purchase_order 테이블에 Insert하는 부분이 있어.
# Insert가 정상적으로 완료되면 DB files 테이블의 상태값(analysis_yn)을 'Y'로 업데이트하는 기능을 추가해줘.
# * [태그:여기에 삽입] 이라고 태그 달아놓은 부분에 넣으면 될 것 같아
@parser.route('/analysis', methods=['POST'])
def process_document_sample():
    print("process_document_sample() called")

    data = request.get_json()
    print(f"Received data: {data}")

    if not data:
        return jsonify({'error': 'No JSON data received'}), 400

    file_id = data.get('id')
    board_id = data.get('board_id')
    filename = data.get('filename')
    filepath = data.get('filepath')

    print(f"Received file ID: {file_id}")
    print(f"Received board ID: {board_id}")
    print(f"Received filename: {filename}")
    print(f"Received filepath: {filepath}")

    if file_id is None or board_id is None or filename is None:
        return jsonify({'error': 'Missing parameters (id, board_id, filename)'}), 400

    # 이제 file_id, board_id, filename을 사용하여 파일 분석 로직을 수행하거나
    # 데이터베이스에서 해당 파일을 찾고 상태를 업데이트할 수 있습니다.

    # 1. Document AI 처리
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    if processor_version_id:
        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        name = client.processor_version_path(
            project_id, location, processor_id, processor_version_id
        )
    else:
        # The full resource name of the processor, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}`
        name = client.processor_path(project_id, location, processor_id)

    # GCS 읽기
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    image_content = blob.download_as_bytes()  # GCS에서 파일 다운로드

    # Load binary data
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # For more information: https://cloud.google.com/document-ai/docs/reference/rest/v1/ProcessOptions
    # Optional: Additional configurations for processing.
    process_options = documentai.ProcessOptions(
        # Process only specific pages
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
            pages=[1]
        )
    )

    # Configure the process request
    request_ai = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
        process_options=process_options,
    )

    result = client.process_document(request=request_ai)

    document = result.document
    print("document.text : ", document.text)

    try:
        # 1) txt 파일로 저장
        # GCS_FILE_PATH_PARSED 폴더 생성
        # if not os.path.exists('./documents_parsed/' + datetime.now().strftime('%Y') + '/' + datetime.now().strftime('%m')): 
        #     os.makedirs('./documents_parsed/' + datetime.now().strftime('%Y') + '/' + datetime.now().strftime('%m'))
        if not os.path.exists(f'./{GCS_FILE_PATH_PARSED}'): 
            os.makedirs(f'./{GCS_FILE_PATH_PARSED}')
            
        parsed_file_name = GCS_FILE_PATH_PARSED + "/" + filename.replace(".pdf", ".txt")
        print("parsed_file_name : ", parsed_file_name)

        # with open(parsed_file_name, "w", encoding="utf-8") as f:
        #     f.write(document.text)
        # print(f"Raw 응답을 '{parsed_file_name}' 파일로 저장했습니다.")

        # 2) GCS에 업로드
        storage_client = storage.Client()

        print(BUCKET_NAME)
        bucket = storage_client.bucket(BUCKET_NAME)

        # print(gcs_file_path)
        # blob = bucket.blob(gcs_file_path)
        # blob = bucket.blob(BUCKET_NAME + GCS_FILE_PATH_PARSED + parsed_file_name)
        blob = bucket.blob(parsed_file_name)

        # print(local_file_name)
        # blob.upload_from_filename(GCS_FILE_PATH_PARSED + parsed_file_name)
        blob.upload_from_filename(parsed_file_name)
        print(f"'{parsed_file_name}' 파일을 gs://{BUCKET_NAME}/{parsed_file_name} 에 업로드했습니다.")

        # 로컬 파일 삭제 (선택 사항)
        # os.remove(local_file_name)
        # print(f"로컬 파일 '{local_file_name}'을 삭제했습니다.")


        # 2. GCS에서 파일 읽기
        # storage_client = storage.Client()
        # bucket = storage_client.bucket(BUCKET_NAME)
        # blob = bucket.blob(gcs_file_path)
        blob = bucket.blob(parsed_file_name)
        file_content = blob.download_as_text(encoding="utf-8")
        # location = "us-central1"  # GCS 버킷의 위치에 맞게 변경하세요. 

        client = genai.Client(vertexai=True, project=project_id, location=LOCATION)

        prompt = """
            \n\n
            아래의 Instruction을 기준으로 검수확인서의 내용을 json으로 변환해줘.

            문서양식1. 검수확인서
                1) 발주처(칼럼명:ordering_company)
                2) 발주담당자(칼럼명:ordering_manager)
                3) 발주일자(칼럼명:order_date)
                4) 발주품목(칼럼명:order_item)
                5) 발주수량(칼럼명:order_quantity)
                6) 발주금액(칼럼명:order_amount)
                7) 주문번호(칼럼명:order_number)
                8) 납품처(칼럼명:delivery_company)
                9) 납품기한(칼럼명:delivery_deadline)
                10) 고객담당자(칼럼명:customer_manager)
            
            ** Instruction **
            1) 이외의 모든 내용은 무시하고 json으로 변환해줘.
            2) **중요 : json 변환 시 key:value에서 key는 반드시 제시된 칼럼명을 사용해줘(DB Insert를 위해 table의 column명과 동일하게 맞춘 상태).
            3) 값이 없는 경우는 null로 변환해줘.
            4) response로 전달하는 내용에 json외 어떠한 데이터나 특수문자도 포함되지 않도록 해줘. jsonify로 바로 변환해서 사용할 수 있도록 해줘.
        """

        contents=f"""
            {prompt}

            여기서부터가 내용의 시작이야.
            {file_content}
            """
        
        print(contents)

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            # contents="Explain bubble sort to me.",
            contents=contents
        )
        
        print(response.text)
        cleaned_data = response.text.replace("```json", "").replace("```", "")
        # json_object = json.loads(cleaned_data)

        try:
            # 1) txt 파일로 저장
            # local_file_name = "document.json"
            # GCS_FILE_PATH_PARSED 폴더 생성
            # if not os.path.exists('./documents_parsed/' + datetime.now().strftime('%Y') + '/' + datetime.now().strftime('%m')): 
            #     os.makedirs('./documents_parsed/' + datetime.now().strftime('%Y') + '/' + datetime.now().strftime('%m'))
            if not os.path.exists(f'./{GCS_FILE_PATH_JSON}'): 
                os.makedirs(f'./{GCS_FILE_PATH_JSON}')
            json_file_name = GCS_FILE_PATH_JSON + "/" + filename.replace(".pdf", ".json")

            with open(json_file_name, "w", encoding="utf-8") as f:
                f.write(cleaned_data)
            print(f"Raw 응답을 '{json_file_name}' 파일로 저장했습니다.")

            # json_file_name = GCS_FILE_PATH_JSON + "/" + "sample_검수확인서_디지월드_한진정보통신_250401.json"

            # 2) GCS에 업로드
            storage_client = storage.Client()
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(json_file_name)
            blob.upload_from_filename(json_file_name)
            print(f"'{json_file_name}' 파일을 gs://{BUCKET_NAME}/{json_file_name} 에 업로드했습니다.")

            # DB Insert
            # JSON 파일 읽기
            with open(json_file_name, 'r', encoding='utf-8') as f: # encoding 추가
                order_data = json.load(f)
            
            try:

                # orders 테이블에 직접 삽입
                conn = get_db_connection()
                cur = conn.cursor()
                now = datetime.now()

                sql = """
                    INSERT INTO purchase_order (board_id, file_id, filepath, created_at, ordering_company, ordering_manager, order_date, order_item, order_quantity, order_amount, order_number, delivery_company, delivery_deadline, customer_manager)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                if order_data.get('order_amount') is not None: 
                    order_amount = str(order_data.get('order_amount')).replace(",", "") 
                else: 
                    order_amount = 0

                cur.execute(sql, (
                    board_id,
                    file_id,
                    filepath,
                    now,
                    order_data.get('ordering_company'),
                    order_data.get('ordering_manager'),
                    order_data.get('order_date'),
                    order_data.get('order_item'),
                    order_data.get('order_quantity'),
                    order_amount,
                    order_data.get('order_number'),
                    order_data.get('delivery_company'),
                    order_data.get('delivery_deadline'),
                    order_data.get('customer_manager'),
                ))

                print(f"주문 데이터가 성공적으로 삽입되었습니다.")

                conn.commit()

                # DB files 테이블의 상태값(analysis_yn)을 'Y'로 업데이트
                update_sql = """
                    UPDATE files
                    SET analysis_yn = 'Y'
                    WHERE id = %s;
                """
                cur.execute(update_sql, (file_id,))
                conn.commit()
                print(f"files 테이블의 analysis_yn이 'Y'로 업데이트되었습니다. file_id: {file_id}")



                # select_sql = """
                #     SELECT id, board_id, file_id, filepath, created_at, ordering_company, ordering_manager, order_date, order_item, order_quantity, order_amount, order_number, delivery_company, delivery_deadline, customer_manager
                #     FROM purchase_order
                #     WHERE board_id = %s;
                # """
                # cur.execute(select_sql, (board_id,))
                # result = cur.fetchall()

                # if result:
                #     analysiss = []
                #     for analysis_row in result:
                #         analysis = {
                #             'ordering_company': analysis_row[5],
                #             'order_date': analysis_row[7],
                #             'order_item': analysis_row[8],
                #             'order_quantity': analysis_row[9],
                #             'order_amount': analysis_row[10]
                #         }
                #         analysiss.append(analysis)

                #     cur.close()
                #     conn.close()

                #     return jsonify(analysiss), 200 # Return the result


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

                    # cur.close()
                    
                return jsonify(boards), 200

                # else:
                #     return jsonify({'error': 'Failed to retrieve order data after insertion'}), 500

            except FileNotFoundError as e:
                print(f"오류: {json_file_name} 파일을 찾을 수 없습니다.")
                result = {"status": "failed", "message": "{}".format(e)}
                return jsonify(result)
            except json.JSONDecodeError as e:
                print(f"오류: JSON 파일 디코딩 실패: {e}")
                result = {"status": "failed", "message": "{}".format(e)}
                return jsonify(result)
            except KeyError as e:
                print(f"오류: JSON 데이터에 필요한 키가 없습니다: {e}")
                result = {"status": "failed", "message": "{}".format(e)}
                return jsonify(result)
            except Exception as e:
                print(f"예상치 못한 오류가 발생했습니다: {e}")
                result = {"status": "failed", "message": "{}".format(e)}
                return jsonify(result)
            finally:
                if conn:
                    conn.close() # Close connection
        
        except Exception as e:
            print(f"오류 발생: {e}")
            result = {"status": "failed", "message": "{}".format(e)}
            return jsonify(result)
        

    except Exception as e:
        print(f"오류 발생: {e}")
        result = {"status": "failed", "message": "{}".format(e)}
        return jsonify(result)
    

    # 임시 응답 (실제 분석 로직 구현 필요)
    # return jsonify({'message': f'Processing file: {filename} (ID: {file_id}, Board ID: {board_id})'}), 200

# prompt:
# 1) process_document_sample()에서 분석이 끝나고 GCS에 파일 업로드까지 끝나면 id와 board_id를 조건으로해서. DB files 테이블의 상태값(analysis_yn)을 'Y'로 업데이트 해줘.

# prompt:
# Document AI API를 호출해서 pdf 문서 내 텍스트를 추출하는 함수인데 
# 이 부분에서 에러가 나고 있어. with open(file_path, "rb") as image: 
# 이게 로컬에서 파일을 읽어오는데 난 GCS에 업로드된 파일을 읽어오고 싶어.
# 소스코드 참고해서 수정해줘.
# @parser.route('/analysis', methods=['POST'])
# def analysis_document_sample():
#     print("process_document_sample() called")
# # def process_document_sample(
# #     project_id: str,
# #     location: str,
# #     processor_id: str,
# #     file_path: str,
# #     mime_type: str,
# #     field_mask: Optional[str] = None,
# #     processor_version_id: Optional[str] = None,
# # ) -> None:
#     # You must set the `api_endpoint` if you use a location other than "us".

#     # 1. Document AI 처리
#     opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

#     client = documentai.DocumentProcessorServiceClient(client_options=opts)

#     if processor_version_id:
#         # The full resource name of the processor version, e.g.:
#         # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
#         name = client.processor_version_path(
#             project_id, location, processor_id, processor_version_id
#         )
#     else:
#         # The full resource name of the processor, e.g.:
#         # `projects/{project_id}/locations/{location}/processors/{processor_id}`
#         name = client.processor_path(project_id, location, processor_id)

#     # Read the file into memory
#     # with open(file_path, "rb") as image:
#     #     image_content = image.read()


#     # GCS 읽기
#     storage_client = storage.Client()
    
#     # file_path 예: "gs://your-bucket/your-file.pdf"
    
#     # match = re.match(r"gs://([^/]+)/(.*)", file_path)
#     # if not match:
#     #     raise ValueError(f"잘못된 GCS URI: {file_path}")
#     # bucket_name, object_name = match.groups()
#     bucket = storage_client.bucket(BUCKET_NAME)
#     blob = bucket.blob(GCS_FILE_PATH)
#     image_content = blob.download_as_bytes()  # GCS에서 파일 다운로드

#     # Load binary data
#     raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

#     # For more information: https://cloud.google.com/document-ai/docs/reference/rest/v1/ProcessOptions
#     # Optional: Additional configurations for processing.
#     process_options = documentai.ProcessOptions(
#         # Process only specific pages
#         individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
#             pages=[1]
#         )
#     )

#     # Configure the process request
#     request = documentai.ProcessRequest(
#         name=name,
#         raw_document=raw_document,
#         field_mask=field_mask,
#         process_options=process_options,
#     )

#     result = client.process_document(request=request)

#     # For a full list of `Document` object attributes, reference this page:
#     # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
#     document = result.document

#     # Read the text recognition output from the processor
#     print("The document contains the following text:")
#     # print(result.document.entity_extraction.form_fields)

#     # return document.text

#     # 2. Document AI 응답 처리 및 GCS 저장
#     """
#     Document AI API의 raw 응답 전체 내용을 txt 파일로 저장하고 GCS에 업로드합니다.

#     Args:
#         raw_response: Document AI API로부터 받은 raw 응답 (문자열).
#         gcs_bucket_name: 업로드할 GCS 버킷 이름.
#         gcs_file_path: GCS에 저장될 파일 경로 (버킷 이름 제외).
#     """
#     try:
#         # 1) txt 파일로 저장
#         local_file_name = "document_ai_raw_response.txt"
#         with open(local_file_name, "w", encoding="utf-8") as f:
#             f.write(document.text)
#         print(f"Raw 응답을 '{local_file_name}' 파일로 저장했습니다.")

#         # 2) GCS에 업로드
#         storage_client = storage.Client()

#         print(gcs_bucket_name)
#         bucket = storage_client.bucket(gcs_bucket_name)

#         print(gcs_file_path)
#         # blob = bucket.blob(gcs_file_path)
#         blob = bucket.blob(GCS_FILE_PATH_PARSED + local_file_name)

#         print(local_file_name)
#         blob.upload_from_filename(local_file_name)
#         print(f"'{local_file_name}' 파일을 gs://{GCS_FILE_PATH_PARSED}/{gcs_file_path} 에 업로드했습니다.")

#         # 로컬 파일 삭제 (선택 사항)
#         # os.remove(local_file_name)
#         # print(f"로컬 파일 '{local_file_name}'을 삭제했습니다.")

#         storage_client = storage.Client()
#         bucket = storage_client.bucket(gcs_bucket_name)
#         blob = bucket.blob(gcs_file_path)
#         file_content = blob.download_as_text(encoding="utf-8")
#         location = "us-central1"  # GCS 버킷의 위치에 맞게 변경하세요. 

#         client = genai.Client(vertexai=True, project=project_id, location=location)

#         prompt = """
#             \n\n
#             아래의 Instruction을 기준으로 검수확인서의 내용을 json으로 변환해줘.

#             문서양식1. 검수확인서
#                 1) 발주처
#                 2) 발주담당자
#                 3) 발주일자
#                 4) 발주품목
#                 5) 발주수량
#                 6) 발주금액
#                 7) 주문번호
#                 8) 납품처
#                 9) 납품기한
#                 10) 고객담당자
            
#             ** Instruction **
#             1) 이외의 모든 내용은 무시하고 json으로 변환해줘.
#             2) json 변환 시 key:value에서 key는 반드시 제시된 영어로 변환해줘(DB Insert를 위해 table의 column명과 동일하게 맞춘 상태).
#             3) 값이 없는 경우는 null로 변환해줘.
#             4) response로 전달하는 내용에 json외 어떠한 데이터나 특수문자도 포함되지 않도록 해줘. jsonify로 바로 변환해서 사용할 수 있도록 해줘.
#         """

#         contents=f"""
#             {prompt}

#             여기서부터가 내용의 시작이야.
#             {file_content}
#             """
        
#         print(contents)

#         response = client.models.generate_content(
#             model="gemini-2.0-flash-001",
#             # contents="Explain bubble sort to me.",
#             contents=contents
#         )
        
#         print(response.text)
#         cleaned_data = response.text.replace("```json", "").replace("```", "")
#         json_object = json.loads(cleaned_data)

#         try:
#             # 1) txt 파일로 저장
#             local_file_name = "document.json"
#             with open(local_file_name, "w", encoding="utf-8") as f:
#                 f.write(cleaned_data)
#             print(f"Raw 응답을 '{local_file_name}' 파일로 저장했습니다.")

#             # 2) GCS에 업로드
#             storage_client = storage.Client()

#             print(gcs_bucket_name)
#             bucket = storage_client.bucket(gcs_bucket_name)

#             print(gcs_file_path_json)
#             blob = bucket.blob(gcs_file_path_json)

#             # local_file_name = "document_ai_raw_response.txt"

#             # print(local_file_name)
#             blob.upload_from_filename(local_file_name)
#             print(f"'{local_file_name}' 파일을 gs://{gcs_bucket_name}/{gcs_file_path_json} 에 업로드했습니다.")
        
#         except Exception as e:
#             print(f"오류 발생: {e}")

#     except Exception as e:
#         print(f"오류 발생: {e}")
    
#     return document.text


# # prompt:
# # 
# @parser.route('/read', methods=['POST'])
# def read_file_from_gcs():
#     """GCS에서 파일을 읽어 내용을 문자열로 반환합니다."""

#     storage_client = storage.Client()
#     bucket = storage_client.bucket(gcs_bucket_name)
#     blob = bucket.blob(gcs_file_path)
#     file_content = blob.download_as_text(encoding="utf-8")
#     location = "us-central1"  # GCS 버킷의 위치에 맞게 변경하세요. 
#     # location = "global"

#     # API_KEY = "AIzaSyD8YpLGhZhNw_Bn13......."

#     # client = genai.Client(vertexai=True, api_key=API_KEY)
#     client = genai.Client(vertexai=True, project=project_id, location=location)

#     prompt = """
#         \n\n
#         아래의 Instruction을 기준으로 검수확인서의 내용을 json으로 변환해줘.

#         문서양식1. 검수확인서
#             1) 발주처
#             2) 발주담당자
#             3) 발주일자
#             4) 발주품목
#             5) 발주수량
#             6) 발주금액
#             7) 주문번호
#             8) 납품처
#             9) 납품기한
#             10) 고객담당자
        
#         ** Instruction **
#         1) 이외의 모든 내용은 무시하고 json으로 변환해줘.
#         2) json 변환 시 key:value에서 key는 반드시 제시된 영어로 변환해줘(DB Insert를 위해 table의 column명과 동일하게 맞춘 상태).
#         3) 값이 없는 경우는 null로 변환해줘.
#         4) response로 전달하는 내용에 json외 어떠한 데이터나 특수문자도 포함되지 않도록 해줘. jsonify로 바로 변환해서 사용할 수 있도록 해줘.
#     """

#     contents=f"""
#         {prompt}

#         여기서부터가 내용의 시작이야.
#         {file_content}
#         """
    
#     print(contents)

#     response = client.models.generate_content(
#         model="gemini-2.0-flash-001",
#         # contents="Explain bubble sort to me.",
#         contents=contents
#     )
    
#     print(response.text)
#     cleaned_data = response.text.replace("```json", "").replace("```", "")
#     json_object = json.loads(cleaned_data)

#     try:
#         # 1) txt 파일로 저장
#         local_file_name = "document.json"
#         with open(local_file_name, "w", encoding="utf-8") as f:
#             f.write(cleaned_data)
#         print(f"Raw 응답을 '{local_file_name}' 파일로 저장했습니다.")

#         # 2) GCS에 업로드
#         storage_client = storage.Client()

#         print(gcs_bucket_name)
#         bucket = storage_client.bucket(gcs_bucket_name)

#         print(gcs_file_path_json)
#         blob = bucket.blob(gcs_file_path_json)

#         # local_file_name = "document_ai_raw_response.txt"

#         # print(local_file_name)
#         blob.upload_from_filename(local_file_name)
#         print(f"'{local_file_name}' 파일을 gs://{gcs_bucket_name}/{gcs_file_path_json} 에 업로드했습니다.")

#         # 로컬 파일 삭제 (선택 사항)
#         # os.remove(local_file_name)
#         # print(f"로컬 파일 '{local_file_name}'을 삭제했습니다.")

#     except Exception as e:
#         print(f"오류 발생: {e}")

#     # return file_content
#     # return response.text
#     return json_object

# 검수확인서
# 주문번호
# HX-PO-15911
# 납품처
# 한진정보통신
# 고객담당자
# 김형곤 차장
# 연락처
# 010-3926-3964
# 용
# 도
# 대한항공 전산장비(아이폰케이블 3m*15 개) 판매
# 품명
# | 세부사양
# 수량
# S/N
# 납품처
# IT1002163
# cable, 케이블, ~ 벨
# 15
# 대한항공
# 킨,~,CAA001bt3MWH^3m
# 상기의 물품을 정히 검수 하였음을 확인합니다.
# 납품장소 : 서울특별시 강서구 대한항공 운항기술팀
# 납품기한 : 2025 년 04 월 15 일납품일 : 2025 년 04월 01일검수일 : 2025 년 04 월 01일
# ※ 품명 및 수량 등을 확인할 수 있도록 사진 필히 첨부 요망
# ※ 납품확인서 첨부
# 검수요청자
# 검수자
# 업 체 : 디지월드
# 업 체 : 한진정보통신
# 담당자 : 안효진
# 담당자 : 김형곤 차장 인
# 신용


# 위 내용에서 아래 항목들만 골라서 json으로 변환해줘.
# 1) 발주처
# 2) 발주담당자
# 3) 발주일자
# 4) 발주품목
# 5) 발주수량
# 6) 발주금액
# 7) 주문번호
# 8) 납품처
# 9) 납품기한
# 10) 고객담당자

# GCS에 업로드된 파일을 읽어서 내가 원하는 json으로 변환해서 DB에 Insert 하는 프로그램을 개발하고 싶은데 아래 Instruction대로 개발 가능한지 확인해줘.
# 1) GCS에 업로드된 파일을 읽기
# 2) 내가 미리 작성한 '프롬프트' 양식에 맞게 변환하도록 LLM API에 요청하기
# 3) LLM API의 응답을 DB에 Insert 하기

# reponse로 받은 값이 아래와 같은데 ```json나 ```같은 문자 제외하고 json만 추출할 수는 없어?
# ```json
# {
#     "발주처": "디지월드",
#     "발주담당자": "안효진",
#     "발주일자": null,
#     "발주품목": "cable, 케이블, ~ 벨\n킨,~,CAA001bt3MWH^3m",
#     "발주수량": 15,
#     "발주금액": null,
#     "주문번호": "HX-PO-15911",
#     "납품처": "한진정보통신",
#     "납품기한": "2025 년 04 월 15 일",
#     "고객담당자": "김형곤 차장"
# }
# ```