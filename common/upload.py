from flask import Flask, request, jsonify, Blueprint
from google.cloud import storage
import os

# app = Flask(__name__)
uploader = Blueprint('uploader', __name__, url_prefix='/api/file')

# Google Cloud Storage 설정
# 환경 변수 또는 보안 파일에서 데이터베이스 연결 정보 로드
from common import getEnv
PROJECT_ID  = getEnv.get_environment_variable('PROJECT_ID')
BUCKET_NAME = getEnv.get_environment_variable('BUCKET_NAME')
print("PROJECT_ID  : ", PROJECT_ID)
print("BUCKET_NAME : ", BUCKET_NAME)

if not PROJECT_ID or not BUCKET_NAME:
    raise ValueError("GCP_PROJECT_ID and GCP_BUCKET_NAME environment variables must be set.")

storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(BUCKET_NAME)


@uploader.route('/upload', methods=['POST'])
def upload_file():
    print("upload_file() called")
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        try:
            blob = bucket.blob(file.filename)
            blob.upload_from_file(file)
            return jsonify({'message': f'File {file.filename} uploaded successfully to gs://{BUCKET_NAME}/{file.filename}'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to upload file: {str(e)}'}), 500

    return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))