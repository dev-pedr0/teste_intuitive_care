from fastapi import FastAPI, Query
from db import conectar_banco

app = FastAPI(title="API Operadoras de Saúde")

@app.get("/api/operadoras")
def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    #Páginas
    offset = (page - 1) * limit

    #Conecta ao banco
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    #Total de registros
    cursor.execute("SELECT COUNT(*) AS total FROM cadastro_operadoras")
    total = cursor.fetchone()["total"]

    #Dados paginados
    cursor.execute(
        """
        SELECT cnpj, registro_operadora, modalidade, uf, status_cadastro
        FROM cadastro_operadoras
        LIMIT %s OFFSET %s
        """,
        (limit, offset)
    )
    operadoras = cursor.fetchall()

    #Desconecta
    cursor.close()
    conn.close()

    #Retornar dados necessários
    return {
        "data": operadoras,
        "total": total,
        "page": page,
        "limit": limit
    }