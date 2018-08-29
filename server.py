from flask import Flask, jsonify, g, Response
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

@app.route('/newuser/<name>', methods=['POST'])
def new_user(name):
    db = get_db()
    queries = (
        '''
        CREATE (le:Person {name:$name})
        RETURN le.name
        '''
                )
    results = db.run(queries, name=name)
    records = []
    for result in results:
        records.append({"name": result["le.name"]})
    return 'Successfully added {} to the database.'.format(records[0]['name'])

@app.route('/users', methods=['GET'])
def get_all_users():
    db = get_db()
    results = db.run("MATCH (name:Person)"
             "RETURN name.name")
    records = []
    for record in results:
        print(record)
        records.append({"name": record["name.name"]})
    return jsonify(records)


app.run(host='0.0.0.0', port=5000)