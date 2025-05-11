from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from userinfo.userinfo import userinfo
from ar.ar_job import ar_job
from ar.ar_info import ar_info
from ar.ar_event import ar_event
from common.log import log, start_scheduler
from common import logger
from common.upload import uploader
from common.parcer import parcer
from common.parser import parser

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://automation-dev-frontend-213242029674.us-central1.run.app"}})
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
CORS(app, resources={r"/api/*": {"origins": "http://0.0.0.0:3000"}})
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3001"}})
CORS(app, resources={r"/api/*": {"origins": "http://0.0.0.0:3001"}})

app.register_blueprint(userinfo)
app.register_blueprint(ar_job)
app.register_blueprint(ar_info)
app.register_blueprint(ar_event)
app.register_blueprint(log)
app.register_blueprint(uploader)
app.register_blueprint(parcer)
app.register_blueprint(parser)

logger.LoggerFactory.create_logger()

@app.route('/', methods=['GET'])
def main():
    return jsonify({'message': 'Hello, World!'})

import socket

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        data = response.json()
        return data['ip']
    except requests.exceptions.RequestException as e:
        print(f"요청 오류 발생: {e}")
        return None

def get_public_ip_alternative():
    try:
        response = requests.get("https://ipinfo.io/ip")
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"요청 오류 발생 (ipinfo.io): {e}")
        return None

def get_local_ip():
    try:
        # 임의의 외부 호스트에 연결 시도
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS
        local_ip = s.getsockname()[0]
    except socket.error as e:
        print(f"소켓 오류 발생: {e}")
        local_ip = None
    finally:
        s.close()
    return local_ip

if __name__ == '__main__':

    # 로컬 IP 주소를 확인하기 위해 get_local_ip() 사용
    ip_address = get_local_ip()

    if ip_address:
        print(f"내 로컬 IP 주소: {ip_address}")
    else:
        print("로컬 IP 주소를 확인하지 못했습니다.")
    
    # 공인 IP 주소를 확인하기 위해 api.ipify.org 사용
    public_ip = get_public_ip()

    if public_ip:
        print(f"내 공인 IP 주소: {public_ip}")
    else:
        public_ip_alt = get_public_ip_alternative()
        if public_ip_alt:
            print(f"내 공인 IP 주소: {public_ip_alt}")
        else:
            print("공인 IP 주소를 확인하지 못했습니다.")

    # app.run(debug=True, port=5000)
    # start_scheduler(app)
    app.run(host='0.0.0.0', port=5000, debug=True)