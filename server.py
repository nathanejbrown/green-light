from flask import Flask, jsonify, g, Response, request
from flask_cors import CORS
from json import dumps

from neo4j.v1 import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "1234"))

app = Flask(__name__)
CORS(app)

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

@app.route('/', methods=['GET'])
def basic_route():
    return 'It works.'

@app.route('/newuser/<name>/<age>/<email>/<password>', methods=['POST'])
def new_user(name, age, email, password):
    db = get_db()
    queries = (
        '''
        CREATE (le:Person {name:$name, age:$age, email:$email, available:False, password:$password})
        RETURN le.name
        '''
                )
    results = db.run(queries, name=name, age=age, email=email, password=password)
    records = []
    for result in results:
        records.append({"name": result["le.name"]})
    return 'Successfully added {} to the database.'.format(records[0]['name'])

@app.route('/users', methods=['GET'])
def get_all_users():
    db = get_db()
    results = db.run(
            '''
            MATCH (r:Person)
            RETURN {id: ID(r), name:r.name, email:r.email, available:r.available, age:r.age, password:r.password} as user
            '''
             )
    records = []
    for record in results:
        records.append({
            'name': record['user']['name'],
            'email': record['user']['email'],
            'age': record['user']['age'],
            'available': record['user']['available'],
            'id': record['user']['id'],
            'password': record['user']['password']
            })
    if not len(records):
        return 'No users found.'
    return jsonify(records)

@app.route('/updateavailability/<email>/<available>', methods=['POST'])
def update_user_availability(email, available):
    db = get_db()
    opposite_available = True
    if (available.lower() == 'true'):
        opposite_available = False
    get_data_query = (
        '''
        MATCH (r:Person {email:$email})
        SET r.available = $available
        RETURN {available:r.available, name:r.name} as user
        '''
    )
    results = db.run(get_data_query, email=email, available=opposite_available)
    records = []
    for result in results:
        records.append({
            'name': result['user']['name'],
            'available': result['user']['available']
        })
    return '{}\'s availability has been set to {}.'.format(records[0]['name'], records[0]['available'])

@app.route('/login', methods=['POST'])
def log_user_in():
    db = get_db()
    values = request.get_json()
    get_data_query = (
        '''
        MATCH (r:Person {email:$email})
        RETURN {password:r.password, name:r.name} as user
        '''
    )
    results = db.run(get_data_query, password=values['password'], email=values['email'])
    records = []
    for result in results:
        print(result)
        records.append({
            'name': result['user']['name'],
            'password': result['user']['password']
        })
    print(records)
    if records[0]['password'] == values['password']:
        return '{} is logged in.'.format(records[0]['name'])
    else:
        return 'Something went wrong.'

app.run(host='0.0.0.0', port=5000)