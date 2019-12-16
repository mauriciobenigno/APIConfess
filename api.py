from flask import Flask
from flask_cors import CORS
import json

app = Flask(__name__)

cors = CORS(app, resource={r"/*":{"origins": "*"}})

posts = [
    {
        'id': 1,
        'texto': 'teste 1',
        'cor': 5,
        'curtidas': 5
    },
    {
        'id': 2,
        'texto': 'teste 2',
        'cor': 5,
        'curtidas': 5
    },
    {
        'id': 3,
        'texto': 'teste 3',
        'cor': 5,
        'curtidas': 5
    },
    {
        'id': 4,
        'texto': ' teste 4',
        'cor': 5,
        'curtidas': 5
    }
]

@app.route('/posts/all', methods=['GET'])
def getAllConfess():
    return jsonify(posts), 200

@app.route('/posts/fav', methods=['GET'])
def getFavConfess():
    return jsonify(posts), 200

@app.route('/posts', methods=['POST'])
def addConfess():
    data = request.get_json()
    posts.append(data)
    return jsonify(data), 201

@app.route('/posts/gen', methods=['POST'])
def genDB():
    return jsonify(data), 201


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()