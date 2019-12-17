import mysql.connector
from mysql.connector import Error

def connect(texto, cor, curtidas):
    """ Connect to MySQL database """
    conn = None
    try:
        conn = mysql.connector.connect(host='us-cdbr-iron-east-05.cleardb.net',
                                       database='heroku_5b193e052a7ad86',
                                       user='bc3024c3520660',
                                       password='41d897e1')
        if conn.is_connected():
            #cursor = conn.cursor()
            #cursor.execute("INSERT INTO heroku_5b193e052a7ad86.postagens (TEXTO_POSTAGEM, COR_ID, NUMERO_CURTIDAS) VALUES ('DDDDDDD', 5, 5)")

            query = "INSERT INTO heroku_5b193e052a7ad86.postagens(TEXTO_POSTAGEM,COR_ID,NUMERO_CURTIDAS) " \
                    "VALUES(%s,%s,%s)"
            args = (texto, cor, curtidas)
         
            cursor = conn.cursor()
            cursor.execute(query, args)
         
            if cursor.lastrowid:
                print('last insert id', cursor.lastrowid)
            else:
                print('last insert id not found')

            conn.commit()

            cursor.execute("SELECT * FROM heroku_5b193e052a7ad86.postagens")
 
            row = cursor.fetchone()
     
            while row is not None:
                print(row[1])
                row = cursor.fetchone()

 
    except Error as e:
        print(e)
 
    finally:
        if conn is not None and conn.is_connected():
            conn.close()


 
 
if __name__ == '__main__':
    connect('Teste','4','6')
