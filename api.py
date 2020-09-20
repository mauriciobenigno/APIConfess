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



############# COISAS DE EMPRESA ####################

@app.route('/empresas', methods=['POST'])
def addEmpresa():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        #prepara a query para o sql
        query = "INSERT INTO fdlc_empresa(fantasia,dtcadastro,descricao,end_lat,end_long) " \
                            "VALUES(%s,%s,%s,%s,%s)"
        args = (data['fantasia'], data['dtcadastro'],data['descricao'],data['end_lat'],data['end_long'])
        #posicionar o cursor no sql    
        cursor = conn.cursor()
        #executa o comando SQL
        cursor.execute(query, args)
        #extrai o ID que foi inserido
        data['codempresa'] = cursor.lastrowid
        #consolida as acoes no SQL
        conn.commit()
        #retorna o objeto para o emitente com o ID bin
        conn.close()
        return jsonify(data), 201

@app.route('/empresas/all', methods=['GET'])
def getAllEmpresas():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        empresas = []
        cursor = conn.cursor()
        cursor.execute('SELECT codempresa,fantasia,descricao,end_lat,end_long FROM fdlc_empresa')
        row = cursor.fetchone()
        while row is not None:
            data = {'codempresa': row[0],'fantasia': row[1],'descricao': row[2],'latitude': row[3],'longitude': row[4]}
            empresas.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(empresas), 200

############# COISAS DE PONTOS ####################

@app.route('/ponto', methods=['POST'])
def addPonto():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        #prepara a query para o sql
        query = "INSERT INTO fdlc_ponto(codusuario,codcampanha,pontuacao,dt_ponto) " \
                            "VALUES(%s,%s,%s,%s,%s)"
        args = (data['codusuario'], data['codcampanha'],data['pontuacao'],data['dt_ponto'])
        #posicionar o cursor no sql    
        cursor = conn.cursor()
        #executa o comando SQL
        cursor.execute(query, args)
        #extrai o ID que foi inserido
        data['codponto'] = cursor.lastrowid
        #consolida as acoes no SQL
        conn.commit()
        #retorna o objeto para o emitente com o ID bin
        conn.close()
        return jsonify(data), 201

@app.route('/ponto/all', methods=['GET'])
def getAllPontos():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        pontos = []
        cursor = conn.cursor()
        cursor.execute('SELECT codponto,codusuario,codcampanha,pontuacao,dt_ponto FROM fdlc_ponto')
        row = cursor.fetchone()
        while row is not None:
            data = {'codponto': row[0],'codusuario': row[1],'codcampanha': row[2],'pontuacao': row[3],'dt_ponto': row[4]}
            pontos.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(pontos), 200

################ COISAS DE CAMPANHA #################

@app.route('/campanhas', methods=['POST'])
def addCampanha():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        #prepara a query para o sql
        query = "INSERT INTO fdlc_campanha (nome,descricao,premio,regra,dt_inicio,dt_fim,meta,alcancado,incremento,pontuado,codempresa,codusuario) " \
                            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        args = (data['nome'], data['descricao'],data['premio'],data['regra'],data['dt_inicio'], data['dt_fim'],data['meta'],data['alcancado'],data['incremento'], data['pontuado'],data['codempresa'],data['codusuario'])
        #posicionar o cursor no sql    
        cursor = conn.cursor()
        #executa o comando SQL  
        cursor.execute(query, args)
        #extrai o ID que foi inserido
        data['codcampanha'] = cursor.lastrowid
        #consolida as acoes no SQL
        conn.commit()
        #retorna o objeto para o emitente com o ID bin
        conn.close()
        return jsonify(data), 201


@app.route('/campanhas/all', methods=['GET'])
def getAllCampanhas():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        empresas = []
        cursor = conn.cursor()
        cursor.execute('SELECT codcampanha,nome,descricao,premio,regra,dt_inicio,dt_fim,meta,alcancado,incremento,pontuado,codempresa,codusuario FROM fdlc_campanha')
        row = cursor.fetchone()
        while row is not None:
            data = {'codcampanha': row[0],
            'nome': row[1],
            'descricao': row[2],
            'premio': row[3],
            'regra': row[4],
            'dt_inicio': row[5],
            'dt_fim': row[6],
            'meta': row[7],
            'alcancado': row[8],
            'incremento': row[9],
            'pontuado': row[10],
            'codempresa': row[11],
            'codusuario': row[12]}
            empresas.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(empresas), 200

############ COISAS DE USUÁRIO ###############

@app.route('/user', methods=['PUT'])
def addUser():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        print("Request Json")
        print(request.json)
        print("Request")
        print(request)
        try:
            data['codusuario']
        except NameError:
            data['codusuario'] = 0

        #Verifica se existe registro
        query = """SELECT CASE WHEN EXISTS (
            SELECT * FROM  fdlc_usuario a
            WHERE  a.codusuario = '{}'
            )
            THEN 1 /* existe*/
            ELSE 0 /* nao existe*/
            END AS resultado""".format(data['codusuario'])
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1: # Retorna usuário existente
            cursor = conn.cursor()
            cursor.execute("SELECT codusuario,nome,sobrenome,cpf,dtnascimento,email,telefone,estado,cidade,cep,image_url,status_cad FROM fdlc_usuario WHERE codusuario ='"+data['codusuario']+"' ;")
            row = cursor.fetchone()
            data = {'codusuario': row[0],
            'nome': row[1],
            'sobrenome': row[2],
            'cpf': row[3],
            'dtnascimento': row[4],
            'email': row[5],
            'telefone': row[6],
            'estado': row[7],
            'cidade': row[8],
            'cep': row[9],
            'image_url': row[10],
            'status_cad': row[11]}
            conn.close()
        else: #Adicionar usuário
        #prepara a query para o sql
            query = "INSERT INTO fdlc_usuario(nome,sobrenome,cpf,dtnascimento,email,telefone,estado,cidade,cep,image_url,status_cad) " \
                                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            args = ('', '','','',data['email'], '','','','', '',false)
            #posicionar o cursor no sql    
            cursor = conn.cursor()
            #executa o comando SQL
            cursor.execute(query, args)
            #extrai o ID que foi inserido
            data['codusuario'] = cursor.lastrowid
            #consolida as acoes no SQL
            conn.commit()
            #retorna o objeto para o emitente com o ID bin
            conn.close()
        #retorna o objeto para o emitente com o id
        return jsonify(data), 201

@app.route('/user', methods=['POST'])
def updateUser():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        #Verifica se existe registro
        query = """SELECT CASE WHEN EXISTS (
            SELECT * FROM  fdlc_usuarios a
            WHERE  a.codusuario = '{}'
            )
            THEN 1 /* existe*/
            ELSE 0 /* nao existe*/
            END AS resultado""".format(data['codusuario'])
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1: # Retorna usuário existente
            cursor = conn.cursor()
            queryUpdate = """ 
            UPDATE fdlc_usuario SET nome = {},sobrenome = {},cpf={},dtnascimento={},email={},telefone={},estado={},cidade={},cep={},image_url={},status_cad={} WHERE codusuario = {}
            """.format(data['nome'],data['sobrenome'],data['cpf'],data['dtnascimento'],data['email'],data['telefone'],data['estado'],data['cidade'],data['cep'],data['image_url'],data['status_cad'],data['codusuario'])
            cursor.execute(queryUpdate)
            row = cursor.fetchone()
            data = {'codusuario': row[0],
            'nome': row[1],
            'sobrenome': row[2],
            'cpf': row[3],
            'dtnascimento': row[4],
            'email': row[5],
            'telefone': row[6],
            'estado': row[7],
            'cidade': row[8],
            'cep': row[9],
            'image_url': row[10],
            'status_cad': row[11]}
            conn.close()
        else: jsonify(data), 401
        return jsonify(data), 200

@app.route('/user/all', methods=['GET'])
def getAllUsers():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        posts = []
        cursor = conn.cursor()
        cursor.execute('SELECT codusuario,nome,sobrenome,cpf,dtnascimento,email,telefone,estado,cidade,cep,image_url FROM fdlc_usuario')
        row = cursor.fetchone()
        while row is not None:
            data = {'codusuario': row[0],
            'nome': row[1],
            'sobrenome': row[2],
            'cpf': row[3],
            'dtnascimento': row[4],
            'email': row[5],
            'telefone': row[6],
            'estado': row[7],
            'cidade': row[8],
            'cep': row[9],
            'image_url': row[10]}
            posts.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(posts), 200

########### INIT E TESTE ##########

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
