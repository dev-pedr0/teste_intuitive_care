from fastapi import FastAPI, HTTPException, Query
from db import conectar_banco

app = FastAPI(title="API Operadoras de Saúde")

#Rota de lista de operadoras
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

#Rota de detalhes por CNPJ
@app.get("/api/operadoras/{cnpj}")
def detalhes_operadora(cnpj: str):
    
    #Conecta ao banco
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    #Busca dados na tabela cadastro_operadoras
    cursor.execute(
        """
        SELECT registro_operadora, modalidade, uf, status_cadastro
        FROM cadastro_operadoras
        WHERE cnpj = %s
        """,
        (cnpj,)
    )
    cadastro = cursor.fetchone()

    #Se não houver dados retorna erro
    if not cadastro:
        raise HTTPException(status_code=404, detail="Operadora não encontrada")

    #Busca dados na tabela despesas operadoras por CNPJ - primeira ocorrência
    cursor.execute(
        """
        SELECT razao_social
        FROM despesas_operadoras
        WHERE cnpj = %s
        ORDER BY created_at ASC
        LIMIT 1
        """,
        (cnpj,)
    )
    razao = cursor.fetchone()

    #Se não houver dados retorna erro
    if not razao:
        raise HTTPException(status_code=404, detail="Razão social não encontrada")

    razao_social = razao["razao_social"]

    #Busca dados na tabela despesas agregadas por razão social
    cursor.execute(
        """
        SELECT
            total_despesas,
            media_t1, media_t2, media_t3,
            desvio_t1, desvio_t2, desvio_t3
        FROM despesas_agregadas
        WHERE razao_social = %s
        """,
        (razao_social,)
    )
    despesas = cursor.fetchone()

    #Se não houver dados retorna erro
    if not despesas:
        raise HTTPException(status_code=404, detail="Despesas agregadas não encontradas")
    
    #Desconecta
    cursor.close()
    conn.close()

    #Retornar dados necessários
    return {
        "status": cadastro["status_cadastro"],
        "razaoSocial": razao_social,
        "cnpj": cnpj,
        "registroAns": cadastro["registro_operadora"],
        "uf": cadastro["uf"],
        "modalidade": cadastro["modalidade"],
        "totalDespesas": despesas["total_despesas"],
        "mediaT1": despesas["media_t1"],
        "mediaT2": despesas["media_t2"],
        "mediaT3": despesas["media_t3"],
        "desvioT1": despesas["desvio_t1"],
        "desvioT2": despesas["desvio_t2"],
        "desvioT3": despesas["desvio_t3"],
    }

#Rota de despesas por CNPJ
@app.get("/api/operadoras/{cnpj}/despesas")
def historico_despesas(cnpj: str):
    
    #Conecta ao banco
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    #Busca despesas em despesas_operadoras
    cursor.execute(
        """
        SELECT
            trimestre,
            ano,
            valor_despesas
        FROM despesas_operadoras
        WHERE cnpj = %s
        ORDER BY ano ASC, trimestre ASC
        """,
        (cnpj,)
    )

    despesas = cursor.fetchall()
    
    #Desconecta
    cursor.close()
    conn.close()

    #Se não houver dados retorna erro
    if not despesas:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma despesa encontrada para esta operadora"
        )
    
    #Retornar dados necessários
    return {
        "cnpj": cnpj,
        "total_registros": len(despesas),
        "despesas": despesas
    }