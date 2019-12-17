import os
from flask import Flask, jsonify, request
from flask_cors import CORS

import mysql.connector
from mysql.connector import Error
import atexit # para fechar a conn com o banco sempre que a api fechar

# Conexão com o SQL
conn = None

def abrirDB():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',
                                       database='heroku_5b193e052a7ad86',
                                       user='bc3024c3520660',
                                       password='41d897e1')
def fecharDB():
    if not conn == None:
        conn.close()
        
atexit.register(fecharDB) #sempre que detectar que o terminal foi fechado, ele executa

# Flask 
app = Flask(__name__)

@app.route('/posts', methods=['POST'])
def addPost():
    if not conn.is_connected():
        abrirDB()
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

@app.route('/users', methods=['POST'])
def addUser():
    if not conn.is_connected():
        abrirDB()
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

@app.route('/users/fav', methods=['POST'])
def addUserFav():
    if not conn.is_connected():
        abrirDB()
    #recebe o objeto json
    data = request.json
    #Adicionar usuário
    query = "INSERT INTO heroku_5b193e052a7ad86.usuariosfavoritos(ID_USUARIO,ID_POST) " \
                    "VALUES(%s,%s)"
    args = (data['usuarioid'],data['postid'])    
    cursor = conn.cursor()
    cursor.execute(query, args)#executa o comando SQL
    conn.commit()#consolida as acoes no SQL
    #retorna o objeto para o emitente com o ID atualizado
    return jsonify(data), 201

@app.route('/posts/all', methods=['GET'])
def getAllConfess():
    if not conn.is_connected():
        abrirDB()
    posts = []
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM heroku_5b193e052a7ad86.postagens')
    row = cursor.fetchone()
    while row is not None:
        data = {'id': row[0],'texto': row[1],'cor': row[2],'curtidas': row[3],'autorid': row[4]}
        posts.append(data)
        row = cursor.fetchone()
    return jsonify(posts), 200

@app.route('/users/all', methods=['GET'])
def getAllUsers():
    if not conn.is_connected():
        abrirDB()
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
    if not conn.is_connected():
        abrirDB()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM heroku_5b193e052a7ad86.usuarios as a WHERE a.APELIDO ='"+apelido+"' ;")
    row = cursor.fetchone()
    data = {'id': row[0],'apelido': row[1]}
    return jsonify(data), 200

@app.route('/users/name/<id>', methods=['GET'])
def getUserName(id):
    if not conn.is_connected():
        abrirDB()
    cursor = conn.cursor()
    cursor.execute("SELECT a.APELIDO FROM heroku_5b193e052a7ad86.usuarios as a WHERE a.ID ='"+id+"' ;")
    row = cursor.fetchone()
    data = row[0]
    return jsonify(data), 200

@app.route('/users/posts/<apelido>', methods=['GET'])
def getUserPosts(apelido):
    if not conn.is_connected():
        abrirDB()
    posts = []
    cursor = conn.cursor()
    query = """SELECT b.* FROM heroku_5b193e052a7ad86.usuarios a
            INNER JOIN heroku_5b193e052a7ad86.postagens b ON b.USUARIO_ID = a.ID
            WHERE a.APELIDO = '{}'""".format(apelido)
    cursor.execute(query)
    row = cursor.fetchone()
    while row is not None:
        data = {'id': row[0],'texto': row[1],'cor': row[2],'curtidas': row[3],'autorid': row[4]}
        posts.append(data)
        row = cursor.fetchone()
    return jsonify(posts), 200

@app.route('/users/favs/<apelido>', methods=['GET'])
def getUserFavs(apelido):
    if not conn.is_connected():
        abrirDB()
    posts = []
    cursor = conn.cursor()
    query = """SELECT c.* FROM heroku_5b193e052a7ad86.usuarios as a
    INNER JOIN heroku_5b193e052a7ad86.usuariosfavoritos as b ON a.ID = b.ID_USUARIO
    INNER JOIN heroku_5b193e052a7ad86.postagens as c ON b.ID_POST = c.ID
    WHERE a.APELIDO = '{}'""".format(apelido)
    cursor.execute(query)
    row = cursor.fetchone()
    while row is not None:
        data = {'id': row[0],'texto': row[1],'cor': row[2],'curtidas': row[3],'autorid': row[4]}
        posts.append(data)
        row = cursor.fetchone()
    return jsonify(posts), 200

@app.route('/teste', methods=['GET'])
def testeSQL():
    if not conn.is_connected():
        abrirDB()
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    row = cursor.fetchone()
    return jsonify("Database version : %s " % row), 200

def main():
    abrirDB()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
