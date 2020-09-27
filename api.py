import os
from flask import Flask, jsonify, request, session
from flask_cors import CORS

import mysql.connector
from mysql.connector import Error
import atexit # para fechar a conn com o banco sempre que a api fechar

from functools import wraps
import jwt
#import datetime
from datetime import datetime, timedelta

# Configs para Token
app = Flask(__name__)
app.secret_key = os.urandom(24)

JWT_SECRET = 'fidelicard'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_DAYS = 365

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


############# COISAS DE TOKEN ####################

def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.args.get('authorization')
        if not token:
            return jsonify({'message': 'Missing token'}), 403
        try:
            data = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        except:
            return jsonify({'message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return wrapped

@app.route('/token', methods=['POST'])
def getToken():
    data = request.json
    payload = {
        'user_id': str(data['email']),
        'exp': datetime.utcnow() + timedelta(days=JWT_EXP_DELTA_DAYS)
    }
    token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
    #token = jwt.encode({
    #    'user': str(data['email']),
    #    'exp': datetime.datetime.utcnow() + datetime.timedelta(days = 365)
    #},
    #app.config["SECRET_KEY"])
    print("chegou aqui 2")
    print(token)
    return jsonify({'token': token.decode('utf-8')})

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
    print("chegou aqui")
    print(request.json)
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

@app.route('/ponto/all', methods=['POST'])
def getAllPontos():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        dataFromApp = request.json
        pontos = []
        cursor = conn.cursor()
        query ='''SELECT p.codponto,p.codusuario,p.codcampanha,p.pontuacao,p.dt_ponto FROM fdlc_ponto p
                            INNER JOIN fdlc_usuario u on u.codusuario = p.codusuario where u.email like '{}'
        '''.format(dataFromApp['email'])

        cursor.execute(query)
        row = cursor.fetchone()
        while row is not None:
            data = {'codponto': row[0],'codusuario': row[1],'codcampanha': row[2],'pontuacao': row[3],'dt_ponto': row[4]}
            pontos.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(pontos), 200

################ COISAS DE CAMPANHA #################

@app.route('/campanhas', methods=['PUT'])
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


@app.route('/campanhas/all', methods=['POST'])
def getAllCampanhas():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        empresas = []
        cursor = conn.cursor()

        dataFromApp = request.json
        cursor = conn.cursor()
        query ='''SELECT c.codcampanha,c.nome,c.descricao,c.premio,c.regra,c.dt_inicio,c.dt_fim,c.meta,c.alcancado,c.incremento,c.pontuado,c.codempresa,c.codusuario FROM fdlc_campanha c 
                            INNER JOIN fdlc_usuario u on u.codusuario = c.codusuario where u.email like '{}'
        '''.format(dataFromApp['email'])

        cursor.execute(query)

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

@app.route('/user/register', methods=['POST'])
def addUser():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        print('TESTEEEEE')
        print(data)
        query = "INSERT INTO fdlc_usuario(nome,sobrenome,cpf,dtnascimento,email,telefone,logradouro,complemento,estado,cidade,cep,image_url,status_cad) " \
                            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        args = ('', '','','',data['email'], '','','','','','', '',False)
        #posicionar o cursor no sql    
        cursor = conn.cursor()
        #executa o comando SQL
        cursor.execute(query, args)
        #extrai o ID que foi inserido
        idUsuario = cursor.lastrowid
        #consolida as acoes no SQL
        conn.commit()
        #retorna o objeto para o emitente com o ID bin
        conn.close()
        #retorna o objeto para o emitente com o id
        if idUsuario > 0:
            return jsonify({'resultado':idUsuario}), 201
        else:
            return jsonify({'resultado':0}), 503

@app.route('/user', methods=['POST'])
def updateUser():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        print(data)
        #Verifica se existe registro
        query = """SELECT CASE WHEN EXISTS ( SELECT * FROM  fdlc_usuario a WHERE  a.email = '{}')
            THEN 1 /* existe*/
            ELSE 0 /* nao existe*/
            END AS resultado""".format(data['email'])
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1: # Retorna usuário existente
            print("usuario existe")
            cursor = conn.cursor()
            queryUpdate = """ 
            UPDATE fdlc_usuario SET nome = '{}',sobrenome = '{}',cpf='{}',dtnascimento='{}',telefone='{}',logradouro='{}',complemento='{}',estado='{}',cidade='{}',cep='{}',image_url='{}',status_cad={} WHERE email = '{}'
            """.format(data['nome'],data['sobrenome'],data['cpf'],data['dtnascimento'],data['telefone'],data['logradouro'],data['complemento'],data['estado'],data['cidade'],data['cep'],data['image_url'],data['status_cad'],data['email'])
            cursor.execute(queryUpdate)
            conn.commit()

            cursor = conn.cursor()
            query ='''SELECT codusuario,nome,sobrenome,cpf,dtnascimento,email,telefone,logradouro,complemento,estado,cidade,cep,image_url,status_cad FROM fdlc_usuario where fdlc_usuario.email = '{}'
            '''.format(data['email'])

            cursor.execute(query)
            result = []
            row = cursor.fetchone()
            while row is not None: 
                newdata = {'codusuario': row[0],'nome': row[1],'sobrenome': row[2],'cpf': row[3],'dtnascimento': row[4],'email': row[5],'telefone': row[6],'logradouro':row[7],'complemento':row[8],'estado': row[9],'cidade': row[10],'cep': row[11], 'image_url': row[12], 'status_cad':row[13]}
                result.append(newdata)
                row = cursor.fetchone()

            print("REsultado: ")
            print(result)

            conn.close()
            return jsonify(result[0]), 201 
        else:
            print("usuario nao existe") 
            jsonify(data), 401
        return jsonify(data), 201

@app.route('/user/login', methods=['POST'])
def getUserFromEmail():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        dataFromApp = request.json

        cursor = conn.cursor()
        query ='''SELECT codusuario,nome,sobrenome,cpf,dtnascimento,email,telefone,logradouro,complemento,estado,cidade,cep,image_url,status_cad FROM fdlc_usuario where fdlc_usuario.email like '{}'
        '''.format(dataFromApp['email'])

        cursor.execute(query)
        row = cursor.fetchone()
        while row is not None:
            data = {'codusuario': row[0],
            'nome': row[1],
            'sobrenome': row[2],
            'cpf': row[3],
            'dtnascimento': row[4],
            'email': row[5],
            'telefone': row[6],
            'logradouro': row[7],
            'complemento': row[8],
            'estado': row[9],
            'cidade': row[10],
            'cep': row[11],
            'image_url': row[12],
            'image_url': row[13]}
            conn.close()
            return jsonify(data), 200

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
