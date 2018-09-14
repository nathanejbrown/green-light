from flask import Flask, jsonify, g, Response, request
from flask_cors import CORS
from json import dumps

from person import Person

import os
import uuid

# from dotenv import load_dotenv
# load_dotenv()

from neo4j.v1 import GraphDatabase

DATABASE_KEY = os.getenv("DATABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", DATABASE_KEY))

app = Flask(__name__)
CORS(app)

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

@app.route('/', methods=['GET'])
def basic_route():
    return 'It works.'

@app.route('/newuser', methods=['POST'])
def new_user():
    values = request.get_json()
    new_person = Person(values['name'], values['age'], values['email'], values['password'])
    result = new_person.add_to_db()
    print (result['error'])
    if result['error']:
        return result['error']
    else:
        return 'Successfully added {} to the database.'.format(result['name'])
        

@app.route('/users', methods=['GET'])
def get_all_users():
    db = get_db()
    results = db.run(
            '''
            MATCH (r:Person)
            RETURN {id: r.unique_id, name:r.name, email:r.email, available:r.available, age:r.age, password:r.password} as user
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

@app.route('/updateavailability', methods=['POST'])
def update_user_availability():
    db = get_db()
    values = request.get_json()
    opposite_available = True
    if (values['available'].lower() == 'true'):
        opposite_available = False
    get_data_query = (
        '''
        MATCH (r:Person {email:$email})
        SET r.available = $available
        RETURN {available:r.available, name:r.name} as user
        '''
    )
    results = db.run(get_data_query, email=values['email'], available=opposite_available)
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

@app.route('/singleuser', methods=['POST'])
def get_user_by_id():
    db = get_db()
    values = request.get_json()
    get_query = (
            '''
            MATCH (r:Person {unique_id:$id})
            RETURN {id: r.unique_id, name:r.name, email:r.email, available:r.available, age:r.age, password:r.password} as user
            '''
             )
    results = db.run(get_query, id=values['id'])
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
    return jsonify(records)


app.run(host='0.0.0.0', port=5000)