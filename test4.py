from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

# FLASK_APP=test4.py flask run
@app.route('/api/example', methods=['POST'])
def example_post():
    # JSON 데이터를 가져옵니다.
    data = request.get_json()
    print(data)

    # 데이터 유효성 검사
    if not data or 'name' not in data or 'age' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    # 데이터 처리 로직
    name = data['name']
    age = data['age']

    # 응답 반환
    return jsonify({
        'message': f'Hello, {name}! Your age is {age}.'
    }), 200

@app.route('/api/getIP', methods=['GET'])
def example_get():
    host = socket.gethostbyname(socket.gethostname()) 
    print(host)

    return host

    


if __name__ == '__main__':
    app.run(debug=True)


# port 지정하는 방법 찾아야함(현재 5000포트 고정)