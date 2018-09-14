import os
import uuid

from flask import g
from neo4j.v1 import GraphDatabase

DATABASE_KEY = os.getenv("DATABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_KEY)

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", DATABASE_KEY))

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

class Person:
    def __init__(self, name, age, email, password, available=False):
        self.name = name
        self.age = age
        self.email = email
        self.password = password
        self.available = available
        self.unique_id = str(uuid.uuid4())
    
    def add_to_db(self):
        db = get_db()
        queries = (
            '''
            CREATE (le:Person {name:$name, age:$age, email:$email, available:False, password:$password, unique_id:$unique_id})
            RETURN le.name
            '''
                    )
        results = db.run(queries, name=self.name, age=self.age, email=self.email, password=self.password, unique_id=str(uuid.uuid4()))
        records = []
        for result in results:
            records.append({"name": result["le.name"]})
        return records[0]['name']


