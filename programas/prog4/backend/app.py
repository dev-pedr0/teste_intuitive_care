from fastapi import FastAPI, HTTPException, Query
from db import conectar_banco
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API Operadoras de Saúde")

#header de requisições
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Rota de lista de operadoras
@app.get("/api/operadoras")
def listar_operadoras(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None)
):
    #Páginas
    offset = (page - 1) * limit

    #Conecta ao banco
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    #Filtros
    filtros = []
    params = []
    if status:
        filtros.append("c.status_cadastro = %s")
        params.append(status)
    if search:
        filtros.append("""
        (
            c.cnpj LIKE %s
            OR d.razao_social LIKE %s
        )
        """)
        params.extend([f"%{search}%", f"%{search}%"])
    where_clause = ""
    if filtros:
        where_clause = "WHERE " + " AND ".join(filtros)

    # Total de registros com razão social
    cursor.execute(f"""
        SELECT COUNT(DISTINCT c.cnpj) AS total
        FROM cadastro_operadoras c
        JOIN despesas_operadoras d ON d.cnpj = c.cnpj
        {where_clause}
    """, params)
    total = cursor.fetchone()["total"]

    #Dados paginados
    cursor.execute(f"""
        SELECT DISTINCT
            c.cnpj,
            d.razao_social,
            c.status_cadastro
        FROM cadastro_operadoras c
        JOIN despesas_operadoras d ON d.cnpj = c.cnpj
        {where_clause}
        ORDER BY d.razao_social ASC
        LIMIT %s OFFSET %s
    """, params + [limit, offset])
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

#Rota que mostra estatísticas gerais
@app.get("/api/estatisticas")
def obter_estatisticas():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    #Top 5 operadoras co maior crescimento percentual de despesas com dados completos
    query_completos = """
    WITH base AS (
        SELECT
            cnpj,
            razao_social,
            trimestre,
            SUM(valor_despesas) AS total_trimestre
        FROM despesas_operadoras
        GROUP BY cnpj, razao_social, trimestre
    ),
    operadoras_completas AS (
        SELECT
            cnpj,
            razao_social
        FROM base
        GROUP BY cnpj, razao_social
        HAVING COUNT(DISTINCT trimestre) = 3
    ),
    limites AS (
        SELECT
            cnpj,
            MIN(trimestre) AS primeiro_trimestre,
            MAX(trimestre) AS ultimo_trimestre
        FROM base
        GROUP BY cnpj
    )
    SELECT
        o.cnpj,
        o.razao_social,
        b1.total_trimestre AS valor_inicial,
        b2.total_trimestre AS valor_final,
        ROUND(
            ((b2.total_trimestre - b1.total_trimestre) / b1.total_trimestre) * 100,
            2
        ) AS crescimento_percentual
    FROM operadoras_completas o
    JOIN limites l ON l.cnpj = o.cnpj
    JOIN base b1 ON b1.cnpj = o.cnpj AND b1.trimestre = l.primeiro_trimestre
    JOIN base b2 ON b2.cnpj = o.cnpj AND b2.trimestre = l.ultimo_trimestre
    ORDER BY crescimento_percentual DESC
    LIMIT 5;
    """
    cursor.execute(query_completos)
    completos = cursor.fetchall()

    #Top 5 operadoras co maior crescimento percentual de despesas com dados incompletos
    query_incompletos = """
    WITH base AS (
        SELECT
            cnpj,
            razao_social,
            trimestre,
            SUM(valor_despesas) AS total_trimestre
        FROM despesas_operadoras
        GROUP BY cnpj, razao_social, trimestre
    ),
    limites_operadora AS (
        SELECT
            cnpj,
            razao_social,
            MIN(trimestre) AS primeiro_trimestre,
            MAX(trimestre) AS ultimo_trimestre,
            COUNT(DISTINCT trimestre) AS trimestres_com_dados
        FROM base
        GROUP BY cnpj, razao_social
        HAVING COUNT(DISTINCT trimestre) < 3
    )
    SELECT
        o.cnpj,
        o.razao_social,
        b1.total_trimestre AS valor_inicial,
        b2.total_trimestre AS valor_final,
        o.trimestres_com_dados,
        (3 - o.trimestres_com_dados) AS trimestres_sem_dados,
        ROUND(
            ((b2.total_trimestre - b1.total_trimestre) / b1.total_trimestre) * 100,
            2
        ) AS crescimento_percentual
    FROM limites_operadora o
    JOIN base b1 ON b1.cnpj = o.cnpj AND b1.trimestre = o.primeiro_trimestre
    JOIN base b2 ON b2.cnpj = o.cnpj AND b2.trimestre = o.ultimo_trimestre
    ORDER BY crescimento_percentual DESC
    LIMIT 5;
    """
    cursor.execute(query_incompletos)
    incompletos = cursor.fetchall()

    #Top 5 estados com maiores despesas
    query_estados = """
    WITH despesas_por_operadora AS (
        SELECT
            uf,
            cnpj,
            SUM(valor_despesas) AS total_operadora
        FROM despesas_operadoras
        WHERE uf IS NOT NULL
        GROUP BY uf, cnpj
    ),
    despesas_por_uf AS (
        SELECT
            uf,
            SUM(total_operadora) AS total_despesas_uf,
            AVG(total_operadora) AS media_despesas_por_operadora
        FROM despesas_por_operadora
        GROUP BY uf
    )
    SELECT
        uf,
        total_despesas_uf,
        media_despesas_por_operadora
    FROM despesas_por_uf
    ORDER BY total_despesas_uf DESC
    LIMIT 5;
    """
    cursor.execute(query_estados)
    estados = cursor.fetchall()

    #Operadoras cusjo gasto ultrapassou sua média trimestral
    query_acima_media = """
    WITH media_geral_operadora AS (
        SELECT
            razao_social,
            uf,
            ROUND(
                (
                    COALESCE(media_t1, 0) +
                    COALESCE(media_t2, 0) +
                    COALESCE(media_t3, 0)
                ) /
                (
                    (media_t1 IS NOT NULL) +
                    (media_t2 IS NOT NULL) +
                    (media_t3 IS NOT NULL)
                ),
                2
            ) AS media_geral
        FROM despesas_agregadas
    ),
    comparacao AS (
        SELECT
            d.cnpj,
            d.razao_social,
            d.trimestre,
            m.media_geral,
            CASE
                WHEN d.valor_despesas > m.media_geral THEN 1
                ELSE 0
            END AS passou
        FROM despesas_operadoras d
        JOIN media_geral_operadora m
            ON m.razao_social = d.razao_social
           AND m.uf = d.uf
    )
    SELECT
        razao_social,
        cnpj,
        media_geral,
        SUM(passou) AS trimestres_acima_da_media
    FROM comparacao
    GROUP BY razao_social, cnpj, media_geral
    HAVING SUM(passou) >= 2
    ORDER BY trimestres_acima_da_media DESC;
    """
    cursor.execute(query_acima_media)
    acima_media = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "crescimento_despesas": {
            "dados_completos": completos,
            "dados_incompletos": incompletos
        },
        "estados_maiores_despesas": estados,
        "operadoras_acima_media": {
            "total": len(acima_media),
            "lista": acima_media
        }
    }
