import os
from flask import Flask, jsonify, request
from flask_cors import CORS

import mysql.connector
from mysql.connector import Error
import atexit # para fechar a conn com o banco sempre que a api fechar

# Conexão com o SQL
conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',
                                       database='heroku_5b193e052a7ad86',
                                       user='bc3024c3520660',
                                       password='41d897e1')
def fecharDB():
    conn.close()
atexit.register(fecharDB) #sempre que detectar que o terminal foi fechado, ele executa

# Flask 
app = Flask(__name__)

@app.route('/posts/all', methods=['GET'])
def getAllConfess():
    posts = []
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM heroku_5b193e052a7ad86.postagens')
    row = cursor.fetchone()
    while row is not None:
        data = {'id': row[0],'texto': row[1],'cor': row[2],'curtidas': row[3],'autorid': row[4]}
        posts.append(data)
        row = cursor.fetchone()
    return jsonify(posts), 200

@app.route('/posts', methods=['POST'])
def addPost():
    #recebe o objeto json
    data = request.json
    #prepara a query para o sql
    query = "INSERT INTO heroku_5b193e052a7ad86.postagens(TEXTO_POSTAGEM,COR_ID,NUMERO_CURTIDAS,USUARIO_ID) " \
                    "VALUES(%s,%s,%s,%s)"
    args = (data['texto'], data['cor'], data['curtidas'],data['autorid'])
    #posicionar o cursor no sql    
    cursor = conn.cursor()
    #executa o comando SQL
    cursor.execute(query, args)
    #extrai o ID que foi inserido
    data['id'] = cursor.lastrowid
    #consolida as acoes no SQL
    conn.commit()
    #retorna o objeto para o emitente com o ID atualizado
    return jsonify(data), 201

@app.route('/user', methods=['POST'])
def addUser():
    #recebe o objeto json
    data = request.json
    #Adicionar usuário
    query = "INSERT INTO heroku_5b193e052a7ad86.usuarios(APELIDO) " \
                    "VALUES(%s)"
    args = (data['apelido'],)    
    cursor = conn.cursor()
    cursor.execute(query, args)#executa o comando SQL
    data['id'] = cursor.lastrowid #extrai o ID que foi inserido e coloca no objeto recebido
    conn.commit()#consolida as acoes no SQL
    #retorna o objeto para o emitente com o ID atualizado
    return jsonify(data), 201

@app.route('/users/all', methods=['GET'])
def getAllUsers():
    posts = []
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM heroku_5b193e052a7ad86.usuarios')
    row = cursor.fetchone()
    while row is not None:
        data = {'id': row[0],'apelido': row[1]}
        posts.append(data)
        row = cursor.fetchone()
    return jsonify(posts), 200

@app.route('/users/<apelido>', methods=['GET'])
def getUser(apelido):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM heroku_5b193e052a7ad86.usuarios as a WHERE a.APELIDO ='"+apelido+"' ;")
    row = cursor.fetchone()
    data = {'id': row[0],'apelido': row[1]}
    return jsonify(data), 200

@app.route('/users/posts/<apelido>', methods=['GET'])
def getUserPosts(apelido):
    posts = []
    cursor = conn.cursor()
    cursor.execute("SELECT b.* FROM heroku_5b193e052a7ad86.usuarios a "\
        "INNER JOIN heroku_5b193e052a7ad86.postagens b ON b.USUARIO_ID = a.ID"\
        "where a.APELIDO = '"+apelido+"'")
    row = cursor.fetchone()
    while row is not None:
        data = {'id': row[0],'texto': row[1],'cor': row[2],'curtidas': row[3],'autorid': row[4]}
        posts.append(data)
        row = cursor.fetchone()
    return jsonify(posts), 200

@app.route('/teste', methods=['GET'])
def testeSQL():
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    row = cursor.fetchone()
    return jsonify("Database version : %s " % row), 200

def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
