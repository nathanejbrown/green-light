from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

fake_data = {
    'picture': 'https://via.placeholder.com/350x350',
    'name': 'Hingle McCringleberry',
    'email': 'hipthrust69@gmail.com'
}

@app.route('/', methods=['GET'])
def basic_route():
    return 'It works.'

@app.route('/userdata', methods=['GET'])
def get_user_data():
    return jsonify(fake_data)

app.run(host='0.0.0.0', port=5000)