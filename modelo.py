data = request.get_json()
VALUES (value1, value2, value3, ...) SELECT LAST_INSERT_ID();
query = """INSERT INTO postagens (TEXTO_POSTAGEM, COR_ID, NUMERO_CURTIDAS)
    VALUES (%s, %s, %s)"""
valores = (data['texto'], data['cor'], data['curtidas'])
cursor.execute(query, valores)
cursor.commit()
cursor.lastrowid
