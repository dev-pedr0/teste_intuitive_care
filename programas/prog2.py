import os
import zipfile
import pandas as pd

from programas.support_code import cnpj_valido, ler_arquivo_com_encoding, registrar_erros

#Caminhos das Pastas:
BASE_DIR = "documents"
PASTA_DOWNLOADS = os.path.join(BASE_DIR, "downloads")
PASTA_EXTRAIDOS = os.path.join(BASE_DIR, "extraidos")
PASTA_NORMALIZADOS = os.path.join(BASE_DIR, "normalizados")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "resultados")

#Meu nome
NOME = "Pedro_Costa"

# Cria todas as pastas de uma vez
os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
os.makedirs(PASTA_EXTRAIDOS, exist_ok=True)
os.makedirs(PASTA_NORMALIZADOS, exist_ok=True)
os.makedirs(PASTA_RESULTADOS, exist_ok=True)

#Menu da atividade 2
def executar():
    while True:
        print("\n=== Atividade 2 ===")
        print("1 - Item 2.1")
        print("2 - Item 2.2")
        print("3 - Item 2.3")
        print("4 - Executar todos")
        print("0 - Sair")
        opcao = input("Escolha: ")

        match opcao:
            case "1":
                print("Iniciando item 2.1")
                atividade21()
            case "2":
                print("Iniciando item 2.2")
                atividade22()
            case "3":
                print("Iniciando item 2.3")
                atividade23()
            case "4":
                print("Iniciando item 2.1")
                atividade21()
                print("Iniciando item 2.2")
                atividade22()
                print("Iniciando item 2.3")
                atividade23()
            case "0":
                print("Fechando atividade 2")
                break
            case _:
                print("Valor inválido")

#Atividade 2.1
def atividade21():
    #Busca os caminhos dos arquivos a serem usados
    caminho_consolidado = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.csv")
    caminho_erros = os.path.join(PASTA_RESULTADOS, "consolidado_despesas_erros.csv")
    
    if not os.path.exists(caminho_consolidado):
        print("Arquivo consolidado_despesas.csv não encontrado.")
        return
    
    #Lê arquivo de despesas
    df = pd.read_csv(caminho_consolidado)

    #Cria coluna de status
    df["Status"] = "OK"

    #Lista para guardar erros únicos
    erros = []

    #Sistema de validações
    linhas_para_remover = []
    for idx, row in df.iterrows():
        problemas = []

        #Validação de cnpj e razão social        
        cnpj = str(row["CNPJ"]).strip()
        cnpj_vazio = (
            not cnpj or
            cnpj.lower() == "nan" or
            "não encontrado" in cnpj.lower()
        )
        razao = str(row["RazaoSocial"]).strip()
        razao_vazia = (
            not razao or
            razao.lower() == "nan" or
            "não encontrado" in razao.lower()
        )

        #Os dois vazios, deleta a linha
        if cnpj_vazio and razao_vazia:
            problemas.append("CNPJ e Razão Social ausentes")
            df.at[idx, "Status"] = "NOK"
            linhas_para_remover.append(idx)
        #Um só vazio informa o erro
        else:
            if cnpj_vazio:
                problemas.append("CNPJ ausente")
                df.at[idx, "Status"] = "NOK"

            elif not cnpj_valido(cnpj):
                problemas.append("CNPJ inválido")
                df.at[idx, "Status"] = "NOK"

            if razao_vazia:
                problemas.append("Razão Social ausente")
                df.at[idx, "Status"] = "NOK"
  
        #Re-validação de valor negativo
        if row["ValorDespesas"] < 0:
            problemas.append("ValorDespesas negativo")
            df.at[idx, "Status"] = "NOK"

        #Re-validação de valor zerado
        if row["ValorDespesas"] == 0:
            problemas.append("ValorDespesas zerado")
            linhas_para_remover.append(idx)

        #Registra cada problema em "erros"
        for problema in problemas:
            erro_registro = {
                "TipoErro": problema,
                "CNPJ": row["CNPJ"],
                "RazaoSocial": row["RazaoSocial"],
                "CNPJsDiferentes": "",
                "Quantidade": "",
                "QuantidadeLinhasAfetadas": "",
                "LinhasAfetadas": "",
                "Detalhes": f"Trimestre: {row['Trimestre']} | ValorDespesas: {row['ValorDespesas']}"
            }
            erros.append(erro_registro)

    registrar_erros(erros, caminho_erros)
    
    #Remove linhas com ValorDespesas zeradas
    if linhas_para_remover:
        df.drop(index=linhas_para_remover, inplace=True)
        df.reset_index(drop=True, inplace=True)
    
    # Salva despesas com a coluna status
    df.to_csv(caminho_consolidado, index=False, encoding="utf-8-sig")
    print(f"Arquivo original atualizado com coluna Status: {caminho_consolidado}")

#Atividade 2.2
def atividade22():
    #Caminhos dos arquivos a serem utilizados
    caminho_despesas = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.csv")
    caminho_ativas = os.path.join(PASTA_DOWNLOADS, "Relatorio_cadop.csv")
    caminho_cancel = os.path.join(PASTA_DOWNLOADS, "Relatorio_cadop_canceladas.csv")
    caminho_erros = os.path.join(PASTA_RESULTADOS, "consolidado_despesas_erros.csv")

    if not os.path.exists(caminho_despesas) or not os.path.exists(caminho_ativas):
        print("Arquivo despesas_consolidadas.csv e/ou relatório de operadoras ativas não encontrados.")
        return
    
    #Lê o arquivo de despesas
    df_despesas = pd.read_csv(caminho_despesas, dtype="str")
    
    #Lê arquivos de empresas ativas e canceladas e concatena as colunas desejadas
    dfs_cadop = []
    for caminho in [caminho_ativas, caminho_cancel]:
        if os.path.exists(caminho):
            print(f"Lendo: {os.path.basename(caminho)}")
            df_temp = ler_arquivo_com_encoding(caminho)

            # Marca a origem do cadastro
            if caminho == caminho_ativas:
                df_temp["StatusCadastro"] = "Ativo"
            else:
                df_temp["StatusCadastro"] = "Cancelado"

            #Testa para saber se as colunas necessárias existem
            colunas_desejadas = ["CNPJ", "REGISTRO_OPERADORA", "Modalidade", "UF", "StatusCadastro"]
            colunas_existentes = [col for col in colunas_desejadas if col in df_temp.columns]
            if len(colunas_existentes) < len(colunas_desejadas):
                faltando = set(colunas_desejadas) - set(colunas_existentes)
                print(f"Aviso: colunas faltando em {os.path.basename(caminho)} → {faltando}")

            # Força CNPJ a ser string (texto)
            if "CNPJ" in df_temp.columns:
                df_temp["CNPJ"] = df_temp["CNPJ"].astype(str).str.strip()

            #Adiciona as colunas desejadas    
            df_temp = df_temp[colunas_existentes]
            dfs_cadop.append(df_temp)

            #Concatena a lista de dataframes em uma só
            df_cadop = pd.concat(dfs_cadop, ignore_index=True)
            df_cadop["CNPJ"] = df_cadop["CNPJ"].astype(str).str.strip()

    #Normaliza formato de CNPJ e cria coluna auxiliar CNPJ_norm no data frame do cadop
    df_cadop["CNPJ_norm"] = df_cadop["CNPJ"].str.replace(r"[./-]", "", regex=True).str.lstrip("0")

    #Prioriza CNPJ do cadastro ativo
    df_cadop["prioridade"] = df_cadop["StatusCadastro"].map({
        "Ativo": 1,
        "Cancelado": 0
    })

    # Detecta CNPJs duplicados no cadastro
    duplicados = df_cadop[df_cadop.duplicated(subset="CNPJ_norm", keep=False)]

    if not duplicados.empty:
        # Agrupa por CNPJ para verificar divergência de dados
        conflitos = (
            duplicados[duplicados["StatusCadastro"] == "Ativo"]
            .groupby("CNPJ_norm")
            .filter(lambda x: x[["REGISTRO_OPERADORA", "Modalidade", "UF"]].nunique().max() > 1)
        )
        if not conflitos.empty:
            erros_cadop = []
            for cnpj, grupo in conflitos.groupby("CNPJ_norm"):
                erros_cadop.append({
                    "TipoErro": "CNPJ duplicado no cadastro com dados divergentes",
                    "CNPJ": cnpj,
                    "RazaoSocial": "",
                    "CNPJsDiferentes": "",
                    "Quantidade": len(grupo),
                    "QuantidadeLinhasAfetadas": len(grupo),
                    "LinhasAfetadas": ", ".join(grupo.index.astype(str)),
                    "Detalhes": (
                        "Registros divergentes no cadastro. "
                        "Utilizado o primeiro registro após deduplicação."
                    )
                })

            registrar_erros(erros_cadop, caminho_erros)

    df_cadop = (
        df_cadop
        .sort_values("prioridade", ascending=False)
        .drop_duplicates(subset="CNPJ_norm", keep="first")
        .drop(columns="prioridade")
    )

    #Normaliza CNPJ no arquivo de despesas e força seu formato em string
    df_despesas["CNPJ"] = (
        df_despesas["CNPJ"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )
    df_despesas["CNPJ_norm"] = df_despesas["CNPJ"].str.replace(r"[./-]", "", regex=True).str.lstrip("0")

    #Verifica CNPJ's vazios
    mask_cnpj_vazio = df_despesas["CNPJ_norm"].isna() | (df_despesas["CNPJ_norm"] == "")
    df_erros_cnpj = df_despesas[mask_cnpj_vazio].copy()
    if not df_erros_cnpj.empty:
        erros_cnpj_vazio = []
        for _, row in df_erros_cnpj.iterrows():
            erros_cnpj_vazio.append({
                "TipoErro": "CNPJ inválido ou não encontrado",
                "CNPJ": "",
                "RazaoSocial": row.get("RazaoSocial", ""),
                "CNPJsDiferentes": "",
                "Quantidade": "",
                "QuantidadeLinhasAfetadas": "",
                "LinhasAfetadas": "",
                "Detalhes": "Registro removido do consolidado por ausência de CNPJ"
            })
        registrar_erros(erros_cnpj_vazio, caminho_erros)      

    # Remove registros com CNPJ vazio do dataframe principal
    df_despesas = df_despesas[~mask_cnpj_vazio]

    #Faz join direto via merge usando CNPJ normalizado
    df_despesas = df_despesas.merge(
        df_cadop[["CNPJ_norm", "REGISTRO_OPERADORA", "Modalidade", "UF"]],
        on="CNPJ_norm",
        how="left"
    )

    #Renomeia coluna para o padrão pedido na atividade
    df_despesas = df_despesas.rename(columns={
        "REGISTRO_OPERADORA": "RegistroANS"
    })

    #Elimina coluna auxiliar
    df_despesas = df_despesas.drop(columns=["CNPJ_norm"], errors="ignore")
    df_cadop = df_cadop.drop(columns=["CNPJ_norm"], errors="ignore")


    #Mantém a coluna status com ultima coluna
    if "Status" in df_despesas.columns:
        cols = [col for col in df_despesas.columns if col != "Status"] + ["Status"]
        df_despesas = df_despesas[cols]

    #Sobrescreve arquivo original
    df_despesas.to_csv(caminho_despesas, index=False, encoding="utf-8-sig")
    print(f"Arquivo atualizado: {caminho_despesas}")

    #Cria arquivo de cadastro normalizado para atividades futuras
    caminho_saida_cadop = os.path.join(PASTA_NORMALIZADOS, "cadastro_operadoras.csv")
    df_cadop.to_csv(
        caminho_saida_cadop,
        index=False,
        encoding="utf-8-sig"
    )
    print(f"Cadastro de operadoras normalizado salvo em: {caminho_saida_cadop}")

#Atividade 2.3
def atividade23():
    #Caminhos para os arquivos que serão utilizados
    caminho_consolidado = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.csv")
    caminho_saida = os.path.join(PASTA_RESULTADOS, "despesas_agregadas.csv")
    caminho_erros = os.path.join(PASTA_RESULTADOS, "consolidado_despesas_erros.csv")

    #Verifica se arquivo de despesas existe
    if not os.path.exists(caminho_consolidado):
        print("Arquivo despesas_consolidadas.csv não encontrado.")
        return
    
    #Lê arquivo de despesas
    df = pd.read_csv(caminho_consolidado)

    # Garante tipos numéricos para cálculos estatísticos
    df["ValorDespesas"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")


    # Normaliza RazaoSocial e UF
    df["RazaoSocial"] = df["RazaoSocial"].astype(str).str.strip().str.upper()  # Remove espaços extras e converte para maiúsculas
    df["UF"] = df["UF"].astype(str).str.strip().str.upper()

    #Validação e verificação de erros
    erros = []
    linhas_para_remover = [] 
    for idx, row in df.iterrows():
        problemas = []

        # Valor nulo ou inválido
        if pd.isna(row["ValorDespesas"]):
            problemas.append("ValorDespesas inválido ou nulo")

        # Valor negativo
        if row["ValorDespesas"] < 0:
            problemas.append("ValorDespesas negativo")

        # Campos chave vazios
        if not str(row["RazaoSocial"]).strip():
            problemas.append("RazaoSocial vazia")
            linhas_para_remover.append(idx)
        if not str(row["UF"]).strip():
            problemas.append("UF vazia")
            linhas_para_remover.append(idx)

        # Registro estruturado de erros
        for problema in problemas:
            erros.append({
                "TipoErro": problema,
                "CNPJ": row.get("CNPJ", ""),
                "RazaoSocial": row.get("RazaoSocial", ""),
                "CNPJsDiferentes": "",
                "Quantidade": "",
                "QuantidadeLinhasAfetadas": "",
                "LinhasAfetadas": str(idx),
                "Detalhes": f"Trimestre: {row.get('Trimestre', '')} | ValorDespesas: {row.get('ValorDespesas', '')}"
            })
    registrar_erros(erros, caminho_erros)
    
    #Remove linhas com UF ou Razão vazias
    if linhas_para_remover:
        df.drop(index=linhas_para_remover, inplace=True)
        df.reset_index(drop=True, inplace=True)
    
    #Agrupa por RazaoSocial, UF e Trimestre para realizar os calculos devidos
    df_trimestre = df.groupby(
        ["RazaoSocial", "UF", "Trimestre"],
        as_index=False
    ).agg(
        Total_Trimestre=("ValorDespesas", "sum"),
        Media_Trimestre=("ValorDespesas", "mean"),
        Desvio_Trimestre=("ValorDespesas", "std")
    )

    #Pivot para médias por trimestre
    media_pivot = df_trimestre.pivot(
        index=["RazaoSocial", "UF"],
        columns="Trimestre",
        values="Media_Trimestre"
    ).reset_index()

    #Pivot para desvios por trimestre
    desvio_pivot = df_trimestre.pivot(
        index=["RazaoSocial", "UF"],
        columns="Trimestre",
        values="Desvio_Trimestre"
    ).reset_index()

    #Total geral de despesas por RazaoSocial e UF
    total_geral = df.groupby(
        ["RazaoSocial", "UF"],
        as_index=False
    ).agg(
        Total_Despesas=("ValorDespesas", "sum")
    )

    #Merge de todas as métricas
    df_agregado = total_geral.merge(
        media_pivot,
        on=["RazaoSocial", "UF"],
        how="left"
    ).merge(
        desvio_pivot,
        on=["RazaoSocial", "UF"],
        how="left"
    )

    #Renomeia colunas para deixar explícito média e desvio por trimestre
    df_agregado = df_agregado.rename(columns={
        "1º Trimestre_x": "Media_1º_Trimestre",
        "2º Trimestre_x": "Media_2º_Trimestre",
        "3º Trimestre_x": "Media_3º_Trimestre",
        "1º Trimestre_y": "Desvio_1º_Trimestre",
        "2º Trimestre_y": "Desvio_2º_Trimestre",
        "3º Trimestre_y": "Desvio_3º_Trimestre",
    })

    #Ordena por despesas decrescente
    df_agregado = df_agregado.sort_values(
        by="Total_Despesas",
        ascending=False
    ).reset_index(drop=True)

    #Criação do arquivo agregado
    df_agregado.to_csv(
        caminho_saida,
        index=False,
        encoding="utf-8-sig"
    )
    print(f"Arquivo criado com sucesso: {caminho_saida}")

    #Criação de arquivo zip
    nome_zip = f"Teste_{NOME}.zip"
    caminho_zip = os.path.join(PASTA_RESULTADOS, nome_zip)

    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(
            caminho_saida,
            arcname=os.path.basename(caminho_saida)
        )
    print(f"Arquivo compactado criado: {caminho_zip}")
