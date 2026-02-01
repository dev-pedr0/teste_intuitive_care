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
        print("2 - Item 3.2")
        print("3 - Item 3.3")
        print("4 - Executar tudo")
        print("0 - Sair")
        opcao = input("Escolha: ")

        match opcao:
            case "1":
                print("Iniciando geração de Tabelas")
                gerar_tabelas()
            case "2":
                print("Iniciando item 3.2")
            case "3":
                print("Iniciando item 3.3")
            case "4":
                print("Iniciando geração de Tabelas")
                gerar_tabelas()
                print("Iniciando item 3.2")
                print("Iniciando item 3.3")
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
    
        #Busca os caminhos dos arquivos a serem usados
        caminho_consolidado = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.csv")
        caminho_agregados = os.path.join(PASTA_RESULTADOS, "despesas_agregadas.csv")
        caminho_cadastro = os.path.join(PASTA_NORMALIZADOS, "cadastro_operadoras.csv")
        caminho_erros = os.path.join(PASTA_RESULTADOS, "consolidado_despesas_erros.csv")

        # =========================
        # Leitura de arquivos
        # =========================

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
        # Correção de Erros
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
        # Normalização de Valores
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
            "4º Trimestre": 4
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
        # Criação de Tabelas
        # =========================
        
        #Tabela de despesas consolidadas
        print("\nCriando tabela de despesas consolidadas")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas_operadoras (
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
            PRIMARY KEY (cnpj),
            INDEX idx_razao_social (razao_social)
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
        ON DUPLICATE KEY UPDATE
            valor_despesas = VALUES(valor_despesas),
            status = VALUES(status)
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