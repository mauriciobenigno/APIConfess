import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql	
import atexit # para fechar a conn com o banco sempre que a api fechar

# Conexão com o SQL
db = pymysql.connect("us-cdbr-iron-east-05.cleardb.net","bc3024c3520660","41d897e1","heroku_5b193e052a7ad86" )
def fecharDB():
    db.close()
atexit.register(fecharDB) #sempre que detectar que o terminal foi fechado, ele executa

# Flask 
app = Flask(__name__)
cors = CORS(app, resource={r"/*":{"origins": "*"}})

@app.route("/", methods=['GET'])
def index():
    return "<h1>Hello World!</h1>"

@app.route("/deploy", methods=['GET'])    
def deploy():
    return "<h1>Testando deploy GitHub x Heroku </h1>"


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

@app.route('/teste', methods=['GET'])
def testeSQL():
    cursor = db.cursor()
    cursor.execute("SELECT VERSION()")
    data = cursor.fetchone()
    #print ("Database version : %s " % data)
    return jsonify("Database version : %s " % data), 200


@app.route('/posts', methods=['POST'])
def addConfess():
	#data = request.json
	#posts.append(data)
    '''cursor = db.cursor()
    query = """INSERT INTO postagens (TEXTO_POSTAGEM, COR_ID, NUMERO_CURTIDAS)
    VALUES (%s, %s, %s)"""
    valores = (data['texto'], data['cor'], data['curtidas'])
    cursor.execute(query, valores)
    cursor.commit()
    cursor.lastrowid
    data['id'] = cursor.lastrowid'''  
    return jsonify(data), 201

@app.route('/posts/gen', methods=['POST'])
def genDB():
    return jsonify(data), 201


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()