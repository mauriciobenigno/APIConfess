from flask import Flask
import json

app = Flask(__name__)

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

@app.route('/', methods=['GET'])
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

