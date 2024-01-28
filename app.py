import json
from datetime import date, datetime
from flask import Flask, Response, request
import psycopg2
import uuid

app = Flask(__name__)

app.url_map.strict_slashes = False

database_conn = {
    "host": "postgres",
    "database": "rinha",
    "user": "rinha",
    "password": "rinha",
    "port": 5432
}


@app.route('/pessoas', methods=['POST'])
def post_pessoas() -> Response:
    """
    atributo	descrição
    apelido	obrigatório, único, string de até 32 caracteres.
    nome	obrigatório, string de até 100 caracteres.
    nascimento	obrigatório, string para data no formato AAAA-MM-DD (ano, mês, dia).
    stack	opcional, vetor de string com cada elemento sendo obrigatório e de até 32 caracteres.
    """

    payload = json.loads(request.data)

    if 'apelido' not in payload or 'nome' not in payload or 'nascimento' not in payload \
            or payload['apelido'] is None or payload['nome'] is None or payload['nascimento'] is None:
        return Response(status=422)

    if (type(payload['apelido']) is not str or len(payload['apelido']) > 32) \
            or (type(payload['nome']) is not str or len(payload['nome']) > 100) \
            or (type(payload['nascimento']) is not str or len(payload['nome']) > 100) \
            or ('stack' in payload and (type(payload['stack']) is not list and payload['stack'] is not None)):
        return Response(status=400)

    try:
        date.fromisoformat(payload['nascimento'])
    except Exception:
        return Response(status=422)

    if 'stack' in payload and type(payload['stack']) is list:
        items = [stk for stk in payload['stack'] if type(stk) is not str or len(stk) > 32]
        if len(items) > 0:
            return Response(status=400)

    nome = payload['nome']
    apelido = payload['apelido']
    nascimento = payload['nascimento']
    stack = payload['stack']

    if type(stack) is list:
        stack = ",".join(stack)

    values = (nome, apelido, nascimento, stack)

    try:
        conn = psycopg2.connect(**database_conn)
        cur = conn.cursor()

        query = """
            INSERT INTO pessoas (id, nome, apelido, nascimento, stack)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (apelido) DO NOTHING;
        """

        pessoa_uuid = str(uuid.uuid4())
        values = (pessoa_uuid,) + values

        cur.execute(query, values)
        conn.commit()

        if cur.rowcount > 0:

            return Response(
                status=201,
                headers={
                    'Content-Type': 'application/json',
                    'Location': f'/pessoas/{pessoa_uuid}'
                }
            )

        cur.close()
        conn.close()

        return Response(status=422)

    except Exception as err:
        return Response(status=500)


@app.route('/pessoas/<id>', methods=['GET'])
def get_pessoas_id(id: str) -> Response:

    try:
        conn = psycopg2.connect(**database_conn)
        cur = conn.cursor()

        query = """
            SELECT id, nome, apelido, nascimento, stack FROM pessoas WHERE id = %s;
        """

        cur.execute(query, (id,))
        conn.commit()

        resultado = cur.fetchone()

        cur.close()
        conn.close()

        pessoa = {
            "id": resultado[0],
            "nome": resultado[1],
            "apelido": resultado[2],
            "nascimento": resultado[3].strftime('%Y-%m-%d'),
            "stack": resultado[4].split(',') if resultado[4] is not None else None
        }

        return Response(
            status=200,
            response=json.dumps(pessoa),
            headers={
                'Content-Type': 'application/json'
            }
        )

    except Exception as err:
        return Response(status=500)

    return Response(status=200)


@app.route('/pessoas', methods=['GET'])
def get_pessoas() -> Response:

    if 't' not in request.args:
        return Response(status=400)

    termo = f"%{request.args['t']}%"

    try:
        conn = psycopg2.connect(**database_conn)
        cur = conn.cursor()

        query = """
            SELECT id, nome, apelido, nascimento, stack 
            FROM pessoas 
            WHERE nome like %s
                or apelido like %s
                or stack like %s;
        """

        cur.execute(query, (termo,termo,termo))
        conn.commit()

        resultado = cur.fetchall()

        cur.close()
        conn.close()

        pessoas: list = []
        for pessoa in resultado:
            pessoas.append(
                {
                    "id": pessoa[0],
                    "nome": pessoa[1],
                    "apelido": pessoa[2],
                    "nascimento": pessoa[3].strftime('%Y-%m-%d'),
                    "stack": pessoa[4].split(',') if pessoa[4] is not None else None
                }
            )

        return Response(
            status=200,
            response=json.dumps(pessoas),
            headers={
                'Content-Type': 'application/json'
            }
        )

    except Exception as err:
        return Response(status=500)


@app.route('/contagem-pessoas', methods=['GET'])
def get_contagem_pessoas() -> Response:

    try:
        conn = psycopg2.connect(**database_conn)
        cur = conn.cursor()

        query = """
            SELECT count(id) as qtd
            FROM pessoas;
        """

        cur.execute(query)
        conn.commit()

        resultado = cur.fetchone()

        cur.close()
        conn.close()

        return Response(
            status=200,
            response=f"{resultado[0]}",
            headers={
                'Content-Type': 'application/json'
            }
        )

    except Exception as err:
        return Response(status=500)


app.run(host='0.0.0.0', debug=True, threaded=True, port=80)
