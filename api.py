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
        query = "INSERT INTO heroku_5b193e052a7ad86.postagens(TEXTO_POSTAGEM,COR_ID,USUARIO_ID,APELIDO) " \
                            "VALUES(%s,%s,%s,%s)"
        args = (data['texto'], data['cor'],data['autorid'],data['apelido'])
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
        #Verifica se existe registro
        query = """SELECT CASE WHEN EXISTS (
            SELECT * FROM  heroku_5b193e052a7ad86.usuarios a
            WHERE  a.APELIDO = '{}'
            )
            THEN 1 /* existe*/
            ELSE 0 /* nao existe*/
            END AS resultado""".format(data['apelido'])
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1: # Retorna usuário existente
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM heroku_5b193e052a7ad86.usuarios as a WHERE a.APELIDO ='"+data['apelido']+"' ;")
            row = cursor.fetchone()
            data = {'id': row[0],'apelido': row[1]}
            conn.close()
        else: #Adicionar usuário
            query = "INSERT INTO heroku_5b193e052a7ad86.usuarios(APELIDO) VALUES('"+data['apelido']+"')"
            cursor = conn.cursor()
            cursor.execute(query)#executa o comando SQL
            data['id'] = cursor.lastrowid #extrai o ID que foi inserido e coloca no objeto recebido
            conn.commit()#consolida as acoes no SQL
        #retorna o objeto para o emitente com o id
        return jsonify(data), 201

@app.route('/empresas/all', methods=['GET'])
def getAllEmpresas():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        empresas = []
        cursor = conn.cursor()
        cursor.execute('SELECT codempresa,fantasia,descricao,end_lat,end_long FROM empresa')
        row = cursor.fetchone()
        while row is not None:
            data = {'codempresa': row[0],'fantasia': row[1],'descricao': row[2],'latitude': row[3],'longitude': row[4]}
            empresas.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(empresas), 200

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
            data = {'id': row[0],'texto': row[1],'cor': row[2],'autorid': row[3],'apelido': row[4]}
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
