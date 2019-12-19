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


def abrirDB():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    
def fecharDB():
    if not conn == None:
        conn.close()
        
atexit.register(fecharDB) #sempre que detectar que o terminal foi fechado, ele executa

# Flask 
app = Flask(__name__)

@app.route('/posts', methods=['POST'])
def addPost():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
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
        #retorna o objeto para o emitente com o ID bin
        conn.close()
        return jsonify(data), 201

@app.route('/users', methods=['POST'])
def addUser():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        #Adicionar usuário
        query = "INSERT INTO heroku_5b193e052a7ad86.usuarios(APELIDO) VALUES('"+data['apelido']+"')"
        cursor = conn.cursor()
        cursor.execute(query)#executa o comando SQL
        data['id'] = cursor.lastrowid #extrai o ID que foi inserido e coloca no objeto recebido
        conn.commit()#consolida as acoes no SQL
        #retorna o objeto para o emitente com o ID atualizado
        return jsonify(data), 201

@app.route('/users/fav', methods=['POST'])
def addUserFav():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
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
        conn.close()
        return jsonify(data), 201

@app.route('/users/like/<usuarioid>/<postid>', methods=['POST'])
def addLike(usuarioid,postid):
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #Verifica se existe registro
        query = """SELECT CASE WHEN EXISTS (
                SELECT * FROM  heroku_5b193e052a7ad86.usuarioslikes a
                WHERE  a.ID_USUARIO = {} AND a.ID_POST = {}
        )
        THEN 1 /* existe*/
        ELSE 0 /* nao existe*/
        END AS resultado""".format(usuarioid,postid)
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM heroku_5b193e052a7ad86.usuarioslikes WHERE ID_USUARIO = '+usuarioid+' AND ID_POST = '+postid)
            cursor = conn.cursor()
            cursor.execute('UPDATE heroku_5b193e052a7ad86.postagens SET NUMERO_CURTIDAS = NUMERO_CURTIDAS-1 WHERE ID = '+postid)
            conn.commit()
        else:
            query = "INSERT INTO heroku_5b193e052a7ad86.usuarioslikes(ID_USUARIO,ID_POST) " \
                                    "VALUES(%s,%s)"
            args = (usuarioid,postid) 
            cursor = conn.cursor()
            cursor.execute(query, args)
            cursor = conn.cursor()
            cursor.execute('UPDATE heroku_5b193e052a7ad86.postagens SET NUMERO_CURTIDAS = NUMERO_CURTIDAS+1 WHERE ID = '+postid)
            conn.commit()
        #retorna o objeto para o emitente com o ID atualizado
        conn.close()
        return jsonify(row[0]), 201

@app.route('/posts/all', methods=['GET'])
def getAllConfess():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        posts = []
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM heroku_5b193e052a7ad86.postagens')
        row = cursor.fetchone()
        while row is not None:
            data = {'id': row[0],'texto': row[1],'cor': row[2],'curtidas': row[3],'autorid': row[4]}
            posts.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(posts), 200

@app.route('/users/all', methods=['GET'])
def getAllUsers():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        posts = []
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM heroku_5b193e052a7ad86.usuarios')
        row = cursor.fetchone()
        while row is not None:
            data = {'id': row[0],'apelido': row[1]}
            posts.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(posts), 200

@app.route('/users/<apelido>', methods=['GET'])
def getUser(apelido):
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM heroku_5b193e052a7ad86.usuarios as a WHERE a.APELIDO ='"+apelido+"' ;")
        row = cursor.fetchone()
        data = {'id': row[0],'apelido': row[1]}
        conn.close()
        return jsonify(data), 200

@app.route('/users/name/<id>', methods=['GET'])
def getUserName(id):
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("SELECT a.APELIDO FROM heroku_5b193e052a7ad86.usuarios as a WHERE a.ID ='"+id+"' ;")
        row = cursor.fetchone()
        data = row[0]
        conn.close()
        return jsonify(data), 200

@app.route('/users/posts/<apelido>', methods=['GET'])
def getUserPosts(apelido):
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
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
        conn.close()
        return jsonify(posts), 200

@app.route('/users/favs/<apelido>', methods=['GET'])
def getUserFavs(apelido):
        conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
        posts = []
        cursor = conn.cursor()
        query = """SELECT b.* FROM heroku_5b193e052a7ad86.usuarios as a
        INNER JOIN heroku_5b193e052a7ad86.usuariosfavoritos as b ON a.ID = b.ID_USUARIO
        WHERE a.APELIDO = '{}'""".format(apelido)
        cursor.execute(query)
        row = cursor.fetchone()
        while row is not None:
            data = {'id': row[0],'usuarioid': row[1],'postid': row[2]}
            posts.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(posts), 200

@app.route('/teste', methods=['GET'])
def testeSQL():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        row = cursor.fetchone()
        conn.close()
        return jsonify("Database version : %s " % row), 200

def main():
    abrirDB()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
