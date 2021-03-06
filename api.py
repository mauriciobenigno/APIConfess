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


############# COISAS DE NUMBER AUTH ####################
@app.route('/number', methods=['POST'])
def checkAndRegisterNumber():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        #recebe o objeto json
        data = request.json
        print(data)
        #Verifica se existe registro
        query = """SELECT CASE WHEN EXISTS ( SELECT * FROM  fdlc_conta_numero a WHERE  a.numero = {})
            THEN 1 /* existe*/
            ELSE 0 /* nao existe*/
            END AS resultado""".format(data['numero'])
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1: # Numero existe, então verifica se está ativo
            print("Conta existe")
            cursor = conn.cursor()
            query =''' SELECT ultima_atividade FROM  fdlc_conta_numero a WHERE  a.numero = '{}'
            '''.format(data['numero'])
            cursor.execute(query)
            resultData = None
            row = cursor.fetchone()
            while row is not None: 
                resultData = {'ultima_atividade': row[0]}
                row = cursor.fetchone()

            # Quando passar aqui,vai verificar se tem 3 meses desde a ultima atividade
           
            #print(resultData['ultima_atividade'])
            #date_time_obj = datetime.strptime(resultData['ultima_atividade'], '%Y-%m-%d %H:%M:%S')
            delta = datetime.now() - resultData['ultima_atividade']
            if delta.days > 90 : # Se tiver acima de 90 dias de diferença, faz update pra cadastrado = false
                print("ultima atividade foi a "+str(delta.days))
                cursor = conn.cursor()
                queryUpdate = """ 
                UPDATE fdlc_conta_numero SET cadastrado = 0 WHERE numero = {}
                """.format(data['numero'])
                cursor.execute(queryUpdate)
                conn.commit()
            else:
                print("ultima atividade foi a "+str(delta.days))

        else: # Numero nao existe, então cria o primeiro registro
            print("Conta  não existe")
            query = "INSERT INTO fdlc_conta_numero(numero,ultima_atividade,cadastrado) " \
                                "VALUES(%s,%s,%s)"
            args = (data['numero'],datetime.now(), 0) # Cadastra o numero, data/hora e seta 0 (false) no cadastrado, pra indicar que precisa preencher o formulario
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()

        # agora faz select no registro e envia pra apk
        print("carregando dados da conta")
        cursor = conn.cursor()
        query ='''SELECT codconta, numero, ultima_atividade, cadastrado, codusuario  FROM fdlc_conta_numero WHERE numero = '{}'
        '''.format(data['numero'])
        cursor.execute(query)
        result = []
        row = cursor.fetchone()
        while row is not None: 
            newdata = {'codconta': row[0],'numero': row[1],'ultima_atividade': row[2],'cadastrado': row[3],'codusuario': row[4]}
            result.append(newdata)
            row = cursor.fetchone()
            jsonify(data), 201
            conn.close()
            return jsonify(result[0]), 201 

        return jsonify(data), 201

@app.route('/number/status', methods=['POST'])
def updateNumberStatus():
    print(request.json)
    dataFromApp = request.json
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        cursor = conn.cursor()
        queryUpdate = """ UPDATE fdlc_conta_numero SET status = '{}'
        """.format(dataFromApp['cadastrado'])
        cursor.execute(queryUpdate)
        conn.commit()
        return jsonify(locais), 201

@app.route('/number/cpf', methods=['POST'])
def checkCpfByNumber():
    print(request.json)
    dataFromApp = request.json
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        # agora faz select no registro e envia pra apk
        cursor = conn.cursor()
        query ='''
        SELECT count(conta.numero) as existe FROM fdlc_conta_numero conta
        INNER JOIN fdlc_usuario usuario on usuario.codusuario = conta.codusuario
        WHERE conta.numero = '{}' AND usuario.cpf like '{}'
        '''.format(dataFromApp['numero'],dataFromApp['cpf'])
        cursor.execute(query)
        resultado = None
        row = cursor.fetchone()
        while row is not None: 
            quantidade = row[0]
            if quantidade > 0:
                resultado = {'resultado':1}
            else: 
                resultado = {'resultado':0}
            row = cursor.fetchone()
        conn.close()
        return jsonify(resultado), 201


############# COISAS DE LOCATION ####################
@app.route('/locais', methods=['POST'])
def getAllLocais():
    print("CHEGOU REQUISICAO AQUI")
    print(request.json)
    dataFromApp = request.json
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        
        locais = []
        cursor = conn.cursor()

        query ='''SELECT codempresa,fantasia,descricao,end_lat,end_long,
                    (6371 * acos( cos( radians({}) ) * cos( radians( end_lat ) ) * cos( radians( end_long ) - radians({}) ) + sin( radians({}) ) * sin( radians(end_lat) ) ) ) AS distancia 
                  FROM fdlc_empresa HAVING distancia < {} order by distancia
        '''.format(dataFromApp['latitude'],dataFromApp['longitude'],dataFromApp['latitude'],dataFromApp['limite'])

        cursor.execute(query)
        row = cursor.fetchone()
        while row is not None:
            data = {'codempresa': row[0],'fantasia': row[1],'descricao': row[2],'end_lat': row[3],'end_long': row[4],'distancia': row[5]}
            locais.append(data)
            row = cursor.fetchone()
        conn.close()
        return jsonify(locais), 201

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
                            INNER JOIN fdlc_usuario u on u.codusuario = p.codusuario where u.codusuario = {}
        '''.format(dataFromApp['codusuario'])

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
                            INNER JOIN fdlc_usuario u on u.codusuario = c.codusuario where u.codusuario = {}
        '''.format(dataFromApp['codusuario'])

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
        query = "INSERT INTO fdlc_usuario(nome,sobrenome,cpf,dtnascimento,email,telefone,logradouro,complemento,bairro,estado,cidade,cep,image_url,status_cad) " \
                            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        args = ('', '','','','',data['telefone'],'','','','','','', '',False)
        #posicionar o cursor no sql    
        cursor = conn.cursor()
        #executa o comando SQL
        cursor.execute(query, args)
        #extrai o ID que foi inserido
        idUsuario = cursor.lastrowid
        #consolida as acoes no SQL
        conn.commit()
        #retorna o objeto para o emitente com o ID bin
        #faz update na conta vinculando o usuário
        print("Vinculando cadastro "+str(idUsuario)+" a conta  "+str(data['telefone']))
        cursor = conn.cursor()
        queryUpdate = """ 
        UPDATE fdlc_conta_numero 
        SET codusuario = {}, 
        cadastrado = 1  
        WHERE numero = {}
        """.format(idUsuario,data['telefone'])
        cursor.execute(queryUpdate)
        conn.commit()

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
        query = """SELECT CASE WHEN EXISTS ( SELECT * FROM  fdlc_usuario a WHERE  a.telefone = '{}')
            THEN 1 /* existe*/
            ELSE 0 /* nao existe*/
            END AS resultado""".format(data['telefone'])
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == 1: # Retorna usuário existente
            print("usuario existe")
            cursor = conn.cursor()
            queryUpdate = """ 
            UPDATE fdlc_usuario SET nome = '{}',sobrenome = '{}',cpf='{}',dtnascimento='{}',email='{}',logradouro='{}',complemento='{}',bairro='{}',estado='{}',cidade='{}',cep='{}',image_url='{}',status_cad={} WHERE telefone = '{}'
            """.format(data['nome'],data['sobrenome'],data['cpf'],data['dtnascimento'],data['email'],data['logradouro'],data['complemento'],data['bairro'],data['estado'],data['cidade'],data['cep'],data['image_url'],data['status_cad'],data['telefone'])
            cursor.execute(queryUpdate)
            conn.commit()

            cursor = conn.cursor()
            query ='''SELECT codusuario,nome,sobrenome,cpf,dtnascimento,email,telefone,logradouro,complemento,bairro,estado,cidade,cep,image_url,status_cad FROM fdlc_usuario where fdlc_usuario.telefone = '{}'
            '''.format(data['telefone'])

            cursor.execute(query)
            result = []
            row = cursor.fetchone()
            while row is not None: 
                newdata = {'codusuario': row[0],'nome': row[1],'sobrenome': row[2],'cpf': row[3],'dtnascimento': row[4],'email': row[5],'telefone': row[6],'logradouro':row[7],'complemento':row[8],'bairro':row[9],'estado': row[10],'cidade': row[11],'cep': row[12], 'image_url': row[13], 'status_cad':row[14]}
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
def getUserFromNumber():
    conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',database='heroku_5b193e052a7ad86',user='bc3024c3520660',password='41d897e1')
    if conn.is_connected():
        dataFromApp = request.json

        cursor = conn.cursor()
        query ='''
        SELECT usuario.codusuario,usuario.nome,usuario.sobrenome,usuario.cpf,usuario.dtnascimento,usuario.email,usuario.telefone,usuario.logradouro,usuario.complemento,usuario.bairro,usuario.estado,usuario.cidade,usuario.cep,usuario.image_url,usuario.status_cad 
        FROM fdlc_usuario usuario
        INNER JOIN fdlc_conta_numero conta ON conta.codusuario =  usuario.codusuario
        WHERE conta.numero = {}
        '''.format(dataFromApp['numero'])

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
            'bairro': row[9],
            'estado': row[10],
            'cidade': row[11],
            'cep': row[12],
            'image_url': row[13],
            'status_cad': row[14]}
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
