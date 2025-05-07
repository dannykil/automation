from google.cloud import documentai as documentai
print("__version__ :" , documentai.__version__)

import os

# from flask import Flask, request, jsonify, Blueprint
from flask import Blueprint
parcer = Blueprint('parcer', __name__, url_prefix='/api/parcer')

from common import getEnv
PROJECT_ID    = getEnv.get_environment_variable('PROJECT_ID')
LOCATION      = getEnv.get_environment_variable('LOCATION')
PROCESSOR_ID  = getEnv.get_environment_variable('PROCESSOR_ID')
GCS_FILE_PATH = getEnv.get_environment_variable('GCS_FILE_PATH')
print("PROJECT_ID  : ", PROJECT_ID)
print("GCS_FILE_PATH  : ", GCS_FILE_PATH)

@parcer.route('/', methods=['POST'])
def process_document_from_gcs():
    """GCS URI를 이용하여 Document AI Form Parser를 호출하고 결과를 반환합니다."""
    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)
    
    gcs_source = documentai.GcsDocument(uri=GCS_FILE_PATH)
    input_config = documentai.InputConfig(
        gcs_source=gcs_source, mime_type="application/pdf"  # 또는 파일 형식에 맞게 변경
    )

    request = documentai.ProcessRequest(
        name=name, document=input_config
    )

    try:
        result = client.process_document(request=request)
        return result.document.entity_extraction.form_fields
    
    except Exception as e:
        print(f"Document AI 처리 오류: {e}")
        return None

# 사용 예시
# PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
# LOCATION = "us-central1"  # Form Parser가 위치한 리전
# PROCESSOR_ID = "YOUR_FORM_PARSER_PROCESSOR_ID"  # Form Parser 프로세서 ID
# GCS_FILE_PATH = "gs://your-bucket-name/path/to/your/document.pdf"

# if __name__ == "__main__":
#     if not PROJECT_ID or not PROCESSOR_ID:
#         print("GCP_PROJECT_ID 또는 Form Parser Processor ID를 설정해주세요.")
#     else:
#         form_fields = process_document_from_gcs(GCS_FILE_PATH, PROJECT_ID, LOCATION, PROCESSOR_ID)
#         if form_fields:
#             print("파싱된 키-값 쌍:")
#             for field in form_fields:
#                 print(f"  {field.field_name.text}: {field.field_value.text}")