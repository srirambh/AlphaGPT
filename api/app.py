from flask import Flask, request
import os
from flask_cors import CORS
import pika
app = Flask(__name__)
CORS(app)
CONNECTIONS = {}

@app.route('/',methods=["GET"])
def hello():
    return {"test" : "good"}

@app.route('/register', methods=["POST"])
def register():
    CONNECTIONS[request.form.get("projectid")] = request.form.get("port") 

@app.route('/project', methods=["GET"])
def getProjects():
    for i in range(len()):

@app.route('/project/create', methods=["POST"])
def createProject():
    #SPIN UP

if __name__ == '__main__':
    port = os.environ.get('FLASK_PORT') or 8080
    port = int(port)
    app.run(port=port,host='0.0.0.0')