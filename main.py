from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from userinfo.user_info import userinfo
from ar.ar_job import ar_job
from ar.ar_info import ar_info
from ar.ar_event import ar_event

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3001"}})

app.register_blueprint(userinfo)
app.register_blueprint(ar_job)
app.register_blueprint(ar_info)
app.register_blueprint(ar_event)

@app.route('/', methods=['GET'])
def main():
    return jsonify({'message': 'Hello, World!'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)