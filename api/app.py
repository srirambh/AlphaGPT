from flask import Flask
import os
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

@app.route('/',methods=["GET"])
def hello():
    return {"test" : "good"}

if __name__ == '__main__':
    port = os.environ.get('FLASK_PORT') or 8080
    port = int(port)
    app.run(port=port,host='0.0.0.0')