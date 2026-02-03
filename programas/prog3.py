import os
import mysql.connector
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from programas.support_code import conectar_banco, registrar_erros

#Caminhos das Pastas
BASE_DIR = "documents"
PASTA_DOWNLOADS = os.path.join(BASE_DIR, "downloads")
PASTA_EXTRAIDOS = os.path.join(BASE_DIR, "extraidos")
PASTA_NORMALIZADOS = os.path.join(BASE_DIR, "normalizados")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "resultados")

def executar():
    while True:
        print("\n=== Atividade 3 ===")
        print("1 - Gerar tabelas")
        print("2 - Query 1 - maior percentual de despesas por operadora")
        print("3 - Query 2 - estados com maior valor de despesas")
        print("4 - Query 3 - operadoras que ultrapassaram sua média de gastos ao menos em 2 trimestres")
        print("5 - Executar todos")
        print("0 - Sair")
        opcao = input("Escolha: ")

        match opcao:
            case "1":
                print("Iniciando geração de Tabelas")
                gerar_tabelas()
            case "2":
                print("Iniciando Query 1")
                consultar_maiores_percentual_despesas()
            case "3":
                print("Iniciando Query 2")
                consultar_estados_maiores_despesas()
            case "4":
                print("Iniciando Query 3")
                consultar_despesas_acima_media()
            case "5":
                print("Iniciando geração de Tabelas")
                gerar_tabelas()
                print("Iniciando Query 1")
                consultar_maiores_percentual_despesas()
                print("Iniciando Query 2")
                consultar_estados_maiores_despesas()
                print("Iniciando Query 3")
                consultar_despesas_acima_media()
            case "0":
                print("Fechando atividade 3")
                break
            case _:
                print("Valor inválido")

#Executa atividade de gerar tabelas
def gerar_tabelas():
    conn = None
    cursor = None
    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        # =========================
        # Ler Arquivos
        # =========================
    
        #Busca os caminhos dos arquivos a serem usados
        caminho_consolidado = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.csv")
        caminho_agregados = os.path.join(PASTA_RESULTADOS, "despesas_agregadas.csv")
        caminho_cadastro = os.path.join(PASTA_NORMALIZADOS, "cadastro_operadoras.csv")
        caminho_erros = os.path.join(PASTA_RESULTADOS, "consolidado_despesas_erros.csv")

        #Lê arquivos
        if not os.path.exists(caminho_consolidado):
            print(f"Arquivo não encontrado: {caminho_consolidado}")
            return
        df_consolidado = pd.read_csv(caminho_consolidado, dtype=str)

        if not os.path.exists(caminho_agregados):
            print(f"Arquivo não encontrado: {caminho_agregados}")
            return
        df_agregadas = pd.read_csv(caminho_agregados, dtype=str)

        if not os.path.exists(caminho_cadastro):
            print(f"Arquivo não encontrado: {caminho_cadastro}")
            return
        df_cadastro = pd.read_csv(caminho_cadastro, dtype=str)

        # =========================
        # Corrigir Erros
        # =========================

        #Verificação de células vazias
        colunas_obrigatorias_consolidadas = [
            "CNPJ",
            "RazaoSocial",
            "Ano",
            "Trimestre",
            "ValorDespesas"
        ]

        colunas_obrigatorias_agregadas = [
            "RazaoSocial",
            "UF",
            "Total_Despesas"
        ]

        colunas_obrigatorias_cadastro = [
            "CNPJ",
            "REGISTRO_OPERADORA",
            "Modalidade",
            "UF",
            "StatusCadastro"
        ]


        # Identifica linhas com valores vazios ou nulos
        mask_vazios_consolidadas = (
            df_consolidado[colunas_obrigatorias_consolidadas]
            .isnull()
            .any(axis=1)
            |
            df_consolidado[colunas_obrigatorias_consolidadas]
            .astype(str)
            .apply(lambda row: row.str.strip().eq("").any(), axis=1)
        )
        df_vazios_consolidadas = df_consolidado[mask_vazios_consolidadas]

        mask_vazios_agregadas = (
            df_agregadas[colunas_obrigatorias_agregadas]
            .isnull()
            .any(axis=1)
            |
            df_agregadas[colunas_obrigatorias_agregadas]
            .astype(str)
            .apply(lambda row: row.str.strip().eq("").any(), axis=1)
        )
        df_vazios_agregadas = df_agregadas[mask_vazios_agregadas]

        mask_vazios_cadastro = (
            df_cadastro[colunas_obrigatorias_cadastro]
            .isnull()
            .any(axis=1)
            |
            df_cadastro[colunas_obrigatorias_cadastro]
            .astype(str)
            .apply(lambda row: row.str.strip().eq("").any(), axis=1)
        )

        df_vazios_cadasttro = df_cadastro[mask_vazios_cadastro]

        #Data frame com todos os erros:
        df_vazios_total = pd.concat(
            [df_vazios_consolidadas, df_vazios_agregadas, df_vazios_cadasttro],
            ignore_index=True
        )

        #Registra erros e remove linhas vazias
        if not df_vazios_total.empty:
            erros = []

            for idx, row in df_vazios_total.iterrows():
                erros.append({
                    "TipoErro": "Campos obrigatórios vazios",
                    "CNPJ": row.get("CNPJ", ""),
                    "RazaoSocial": row.get("RazaoSocial", ""),
                    "Quantidade": 1,
                    "QuantidadeLinhasAfetadas": 1,
                    "LinhasAfetadas": idx,
                    "Detalhes": (
                        "Campos vazios detectados → "
                        + ", ".join([
                            col for col in colunas_obrigatorias_consolidadas
                            if pd.isna(row[col]) or str(row[col]).strip() == ""
                        ])
                    )
                })
            registrar_erros(erros, caminho_erros)
            df_consolidado = df_consolidado[~mask_vazios_consolidadas].copy()
            df_agregadas = df_agregadas[~mask_vazios_agregadas].copy()
            df_cadastro = df_cadastro[~mask_vazios_cadastro].copy()

        # =========================
        # Normalizar Valores
        # =========================

        #Normaliza cnpj
        df_consolidado["CNPJ"] = (
            df_consolidado["CNPJ"]
            .str.replace(r"[./-]", "", regex=True)
            .str.strip()
        )

        df_cadastro["CNPJ"] = (
            df_cadastro["CNPJ"]
            .str.replace(r"[./-]", "", regex=True)
            .str.strip()
        )

        #Converte ano para valor numérico
        df_consolidado["Ano"] = df_consolidado["Ano"].astype(int)

        #Converte colunas monetárias para decimal
        df_consolidado["ValorDespesas"] = (
            df_consolidado["ValorDespesas"]
            .str.replace(",", ".", regex=False)
            .apply(lambda x: Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        )

        colunas_monetarias = [
            "Total_Despesas",
            "Media_1º_Trimestre",
            "Media_2º_Trimestre",
            "Media_3º_Trimestre",
            "Desvio_1º_Trimestre",
            "Desvio_2º_Trimestre",
            "Desvio_3º_Trimestre"
        ]
        for col in colunas_monetarias:
            df_agregadas[col] = (
                df_agregadas[col]
                .str.replace(",", ".", regex=False)
                .apply(lambda x: Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            )

        #Converte trimestre para número
        mapa_trimestre = {
            "1º Trimestre": 1,
            "2º Trimestre": 2,
            "3º Trimestre": 3,
        }
        df_consolidado["trimestre"] = df_consolidado["Trimestre"].map(mapa_trimestre)

        #Converte valores NaN em None
        df_consolidado = df_consolidado.where(pd.notna(df_consolidado), None)
        df_agregadas   = df_agregadas.where(pd.notna(df_agregadas), None)
        df_cadastro    = df_cadastro.where(pd.notna(df_cadastro), None)

        # =========================
        # Operação Específica - Normalização agressiva e remoção de duplicadas em Razão social do arquivo de despesas agregadas
        # =========================
       
        #Normalização agressiva da razão social ANTES de qualquer outra operação
        print("Normalizando RazaoSocial para evitar falsos diferentes...")
        df_agregadas["RazaoSocial_original"] = df_agregadas["RazaoSocial"]  # backup para debug

        df_agregadas["RazaoSocial"] = (
            df_agregadas["RazaoSocial"]
            .astype(str)
            .str.normalize('NFKD')                     # decompõe acentos
            .str.encode('ascii', errors='ignore')      # remove acentos
            .str.decode('ascii')
            .str.lower()                               # tudo minúsculo
            .str.replace(r'\s+', ' ', regex=True)      # múltiplos espaços → um só
            .str.strip()                               # remove espaços laterais
        )

        #Mostrar se houve alterações reais
        alterados = df_agregadas["RazaoSocial_original"] != df_agregadas["RazaoSocial"]
        if alterados.any():
            print("→ Algumas RazaoSocial foram normalizadas. Exemplos:")
            print(df_agregadas[alterados][["RazaoSocial_original", "RazaoSocial"]].head(8))
        else:
            print("→ Nenhuma alteração detectada na normalização (pode ser bom sinal ou encoding idêntico)")

        #Identifica duplicatas na chave primária de agregados
        print("Removendo duplicatas reais na chave primária (RazaoSocial + UF)...")
        antes = len(df_agregadas)
        #Mantém apenas a PRIMEIRA ocorrência de cada
        df_agregadas = df_agregadas.drop_duplicates(
            subset=["RazaoSocial", "UF"],
            keep="first"
        ).copy()
        depois = len(df_agregadas)
        diferenca = antes - depois
        if diferenca > 0:
            print(f"→ Removidas {diferenca} linhas duplicadas na chave primária")
            # Registra no log de erros
            erros_chave = [{
                "TipoErro": "Duplicatas removidas na chave primária",
                "CNPJ": "",
                "RazaoSocial": "Várias",
                "Quantidade": diferenca,
                "QuantidadeLinhasAfetadas": diferenca,
                "LinhasAfetadas": "—",
                "Detalhes": f"Removidas {diferenca} duplicatas (mantida a primeira ocorrência de cada grupo RazaoSocial+UF)"
            }]
            registrar_erros(erros_chave, caminho_erros)
        else:
            print("→ Nenhuma duplicata na chave primária encontrada")

        # =========================
        # Cariar Tabelas
        # =========================
        
        #Tabela de despesas consolidadas
        print("\nCriando tabela de despesas consolidadas")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas_operadoras (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            cnpj CHAR(14) NOT NULL,
            razao_social VARCHAR(255) NOT NULL,
            trimestre TINYINT NOT NULL,
            ano SMALLINT NOT NULL,
            valor_despesas DECIMAL(15,2) NOT NULL,
            registro_ans VARCHAR(20),
            modalidade VARCHAR(100),
            uf CHAR(2),
            status VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_cnpj (cnpj),
            INDEX idx_cnpj_ano_trimestre (cnpj, ano, trimestre)
        )
        """)

        cursor.execute("TRUNCATE TABLE despesas_operadoras")
        print("Tabela criada com sucesso!")

        #Tabela de despesas agregadas
        print("Criando tabela de despesas agregadas")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas_agregadas (
            razao_social VARCHAR(255) NOT NULL,
            uf CHAR(2) NOT NULL,
            total_despesas DECIMAL(18,2) NOT NULL,
            media_t1 DECIMAL(18,2),
            media_t2 DECIMAL(18,2),
            media_t3 DECIMAL(18,2),
            desvio_t1 DECIMAL(18,2),
            desvio_t2 DECIMAL(18,2),
            desvio_t3 DECIMAL(18,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (razao_social, uf)
        )
        """)
        cursor.execute("TRUNCATE TABLE despesas_agregadas")
        print("Tabela criada com sucesso!")

        #Tabela de cadastros
        print("Criando tabela de cadastro")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cadastro_operadoras (
            cnpj CHAR(14) NOT NULL,
            registro_operadora VARCHAR(20) NOT NULL,
            modalidade VARCHAR(100),
            uf CHAR(2),
            status_cadastro VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (cnpj)
        )
        """)
        cursor.execute("TRUNCATE TABLE cadastro_operadoras")
        print("Tabela criada com sucesso!")

        #Importa os dados consolidados
        sql_insert = """
        INSERT INTO despesas_operadoras (
            cnpj,
            razao_social,
            trimestre,
            ano,
            valor_despesas,
            registro_ans,
            modalidade,

            uf,
            status
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        dados = [
            (
                row["CNPJ"],
                row["RazaoSocial"],
                row["trimestre"],
                row["Ano"],
                row["ValorDespesas"],
                row["RegistroANS"],
                row["Modalidade"],
                row["UF"],
                row["Status"]
            )
            for _, row in df_consolidado.iterrows()
        ]
        cursor.executemany(sql_insert, dados)
        conn.commit()
        print("\nDespesas consolidadas inseridas com sucesso")

        #Importa os dados agregados
        sql_insert = """
        INSERT INTO despesas_agregadas (
            razao_social,
            uf,
            total_despesas,
            media_t1,
            media_t2,
            media_t3,
            desvio_t1,
            desvio_t2,
            desvio_t3
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        dados = [
            (
                row["RazaoSocial"],
                row["UF"],
                row["Total_Despesas"],
                row["Media_1º_Trimestre"],
                row["Media_2º_Trimestre"],
                row["Media_3º_Trimestre"],
                row["Desvio_1º_Trimestre"],
                row["Desvio_2º_Trimestre"],
                row["Desvio_3º_Trimestre"]
            )
            for _, row in df_agregadas.iterrows()
        ]
        cursor.executemany(sql_insert, dados)
        conn.commit()
        print("Despesas agregadas inseridas com sucesso")

        #Importa os dados de cadastro
        sql_insert = """
        INSERT INTO cadastro_operadoras (
            cnpj,
            registro_operadora,
            modalidade,
            uf,
            status_cadastro
        ) VALUES (%s,%s,%s,%s,%s)
        """
        dados = [
            (
                row["CNPJ"],
                row["REGISTRO_OPERADORA"],
                row["Modalidade"],
                row["UF"],
                row["StatusCadastro"]
            )
            for _, row in df_cadastro.iterrows()
        ]
        cursor.executemany(sql_insert, dados)
        conn.commit()
        print("Dados de cadastro inseridos com sucesso")

    except mysql.connector.Error as err:
        print("Erro ao conectar:", err)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

#Executa query para operadoras com maior crescimento percentual de despesas entre o primeiro e o último trimestre analisado
def consultar_maiores_percentual_despesas():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    # Query 1 — operdoras com dados completos
    query_completos = """
    WITH trimestres_periodo AS (
        SELECT COUNT(DISTINCT trimestre) AS total_trimestres
        FROM despesas_operadoras
    ),
    base AS (
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
            b.cnpj,
            b.razao_social
        FROM base b
        GROUP BY b.cnpj, b.razao_social
        HAVING COUNT(DISTINCT b.trimestre) = 3
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
    JOIN base b1
        ON b1.cnpj = o.cnpj
    AND b1.trimestre = l.primeiro_trimestre
    JOIN base b2
        ON b2.cnpj = o.cnpj
    AND b2.trimestre = l.ultimo_trimestre
    ORDER BY crescimento_percentual DESC
    LIMIT 5;
    """
    cursor.execute(query_completos)
    resultado_completos = cursor.fetchall()

    # Query 2 — operdoras com dados incompletos
    query_incompletos = """
    WITH trimestres_periodo AS (
        SELECT COUNT(DISTINCT trimestre) AS total_trimestres
        FROM despesas_operadoras
    ),
    base AS (
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
            b.cnpj,
            b.razao_social,
            MIN(b.trimestre) AS primeiro_trimestre,
            MAX(b.trimestre) AS ultimo_trimestre,
            COUNT(DISTINCT b.trimestre) AS trimestres_com_dados
        FROM base b
        GROUP BY b.cnpj, b.razao_social
    ),
    operadoras_incompletas AS (
        SELECT
            l.*,
            (3 - l.trimestres_com_dados) AS trimestres_sem_dados
        FROM limites_operadora l
        CROSS JOIN trimestres_periodo tp
        WHERE l.trimestres_com_dados < 3
    )
    SELECT
        o.cnpj,
        o.razao_social,
        b1.total_trimestre AS valor_inicial,
        b2.total_trimestre AS valor_final,
        o.trimestres_com_dados,
        o.trimestres_sem_dados,
        ROUND(
            ((b2.total_trimestre - b1.total_trimestre) / b1.total_trimestre) * 100,
            2
        ) AS crescimento_percentual
    FROM operadoras_incompletas o
    JOIN base b1
        ON b1.cnpj = o.cnpj
    AND b1.trimestre = o.primeiro_trimestre
    JOIN base b2
        ON b2.cnpj = o.cnpj
    AND b2.trimestre = o.ultimo_trimestre
    ORDER BY crescimento_percentual DESC
    LIMIT 5;
    """
    cursor.execute(query_incompletos)
    resultado_incompletos = cursor.fetchall()

    #Fecha conexões
    cursor.close()
    conn.close()

    #Mostra em console
    print("\n5 operadoras com maior crescimento percentual de despesas (dados completos)")
    if resultado_completos:
        for r in resultado_completos:
            print(r)
    else:
        print("Nenhuma operadora com dados completos encontrada.")

    print("\n5 operadoras com maior crescimento percentual de despesas (dados incompletos)")
    if resultado_incompletos:
        for r in resultado_incompletos:
            print(r)
    else:
        print("Nenhuma operadora com dados incompletos encontrada.")

    #Retorna dados para uso em outros códigos
    return {
        "dados_completos": resultado_completos,
        "dados_incompletos": resultado_incompletos
    }

#Executa query para estados com maiores despesas
def consultar_estados_maiores_despesas():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    #Realização da query
    query = """
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
    cursor.execute(query)
    resultado = cursor.fetchall()

    #Mostra em console
    print("\n5 estados com maiores despesas:")
    if resultado:
        for r in resultado:
            print(r)
    else:
        print("Nenhum estado encontrado")


    #Retorna dados para uso em outros códigos
    return resultado

#Executa query para despesas que ultrapassaram a média por operadora
def consultar_despesas_acima_media():
    conn = conectar_banco()
    cursor = conn.cursor(dictionary=True)

    #Realização da query
    query = """
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
    comparacao_trimestre AS (
        SELECT
            d.cnpj,
            d.razao_social,
            d.trimestre,
            m.media_geral,
            MAX(
                CASE
                    WHEN d.valor_despesas > m.media_geral THEN 1
                    ELSE 0
                END
            ) AS passou_no_trimestre
        FROM despesas_operadoras d
        JOIN media_geral_operadora m
            ON m.razao_social = d.razao_social
        AND m.uf = d.uf
        GROUP BY
            d.cnpj,
            d.razao_social,
            d.trimestre,
            m.media_geral
    )
    SELECT
        razao_social,
        cnpj,
        media_geral,
        SUM(passou_no_trimestre) AS trimestres_acima_da_media
    FROM comparacao_trimestre
    GROUP BY
        razao_social,
        cnpj,
        media_geral
    HAVING SUM(passou_no_trimestre) >= 2
    ORDER BY trimestres_acima_da_media DESC;
    """
    cursor.execute(query)
    resultado = cursor.fetchall()

    #Soma o total de operadoras que ultrapassaram
    total_operadoras = len(resultado)
    
    #Mostra em console
    print("\n Registro de ultrapassagem, em pelo menos 2 trimestres, de valor de despesa da média geral por operadora:")
    if resultado:
        for r in resultado:
            print(r)
        print(f"Total de Operadoras:{total_operadoras}")
    else:
        print("Nenhuma registro encontrado")


    #Retorna dados para uso em outros códigos
    return {
        "resultado": resultado,
        "total_operadoras": total_operadoras
    }