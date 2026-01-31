import os
import pandas as pd
from openpyxl import load_workbook

from programas.support_code import cnpj_valido, ler_arquivo_com_encoding, registrar_erros

#Caminhos das Pastas:
BASE_DIR = "documents"
PASTA_DOWNLOADS = os.path.join(BASE_DIR, "downloads")
PASTA_EXTRAIDOS = os.path.join(BASE_DIR, "extraidos")
PASTA_NORMALIZADOS = os.path.join(BASE_DIR, "normalizados")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "resultados")

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

        #Validação do CNPJ
        cnpj = str(row["CNPJ"]).strip()
        if "não encontrado" in cnpj.lower() or not cnpj_valido(cnpj):
            problemas.append("CNPJ inválido ou não encontrado")
            df.at[idx, "Status"] = "NOK"
        
        #Validação de Razão Social
        razao = str(row["RazaoSocial"]).strip()
        if not razao or "não encontrado" in razao.lower() or razao.lower() == "nan":
            problemas.append("Razão Social vazia ou não encontrada")
            df.at[idx, "Status"] = "NOK"
        
        #Re-validação de valor negativo
        if row["ValorDespesas"] < 0:
            problemas.append("ValorDespesas negativo")
            df.at[idx, "Status"] = "NOK"

        #Re-validação de valor zerado
        if row["ValorDespesas"] == 0:
            problemas.append("ValorDespesas zerado")
            df.at[idx, "Status"] = "NOK"
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

            #Testa para saber se as colunas necessárias existem
            colunas_desejadas = ["CNPJ", "REGISTRO_OPERADORA", "Modalidade", "UF"]
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

    # Detecta CNPJs duplicados no cadastro
    duplicados = df_cadop[df_cadop.duplicated(subset="CNPJ_norm", keep=False)]

    if not duplicados.empty:
        # Agrupa por CNPJ para verificar divergência de dados
        conflitos = (
            duplicados
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

    df_cadop = df_cadop.drop_duplicates(subset="CNPJ_norm", keep="first")

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

    #Mantém a coluna status com ultima coluna
    if "Status" in df_despesas.columns:
        cols = [col for col in df_despesas.columns if col != "Status"] + ["Status"]
        df_despesas = df_despesas[cols]

    #Sobrescreve arquivo original
    df_despesas.to_csv(caminho_despesas, index=False, encoding="utf-8-sig")
    print(f"Arquivo atualizado: {caminho_despesas}")



#Atividade 2.3
def atividade23():
    #=====================#
    #Parte 1 - Agrupamento Correto do documento
    #=====================#

    #Caminhos para os arquivos que serão utilizados
    caminho_original = os.path.join(PASTA_RESULTADOS, "despesas_consolidadas.csv")
    caminho_novo = os.path.join(PASTA_RESULTADOS, "despesas_consolidadas_agrupado.csv")
    caminho_erros = os.path.join(PASTA_RESULTADOS, "despesas_consolidadas_erros.xlsx")

    #Verifica se arquvio de despesas existe
    if not os.path.exists(caminho_original):
        print("Arquivo despesas_consolidadas.csv não encontrado.")
        return
    
    #Lê arquivo de despesas
    df = pd.read_csv(caminho_original, dtype=str)

    # Verifica se os dados já estão agrupado por RazaoSocial e UF
    agrupamento = df.groupby(["RazaoSocial", "UF"]).size().reset_index(name="contagem")
    nao_agrupado = agrupamento[agrupamento["contagem"] > 1]

    #Se os dados já estiverem agrupados corretamente o código encerra
    if nao_agrupado.empty:
        print("Os dados já estão agrupados por RazaoSocial + UF.")
        return

    print(f"Dados NÃO estão agrupados. Encontradas {len(nao_agrupado)} combinações duplicadas.")

    #Verifica a presença de erros antes de agrupar, como modalidades dfiferentes no mesmo cnpj
    erros = []
    grupos = df.groupby(["RazaoSocial", "UF"])
    for nome_grupo, grupo in grupos:
        if len(grupo) > 1:
            if grupo["CNPJ"].nunique() > 1:
                erros.append({
                    "CNPJ": grupo["CNPJ"].iloc[0],
                    "RazaoSocial": nome_grupo[0],
                    "Trimestre": grupo["Trimestre"].iloc[0],  # mostra um exemplo
                    "ValorDespesas": grupo["ValorDespesas"].sum(),
                    "TipoErro": "CNPJ diferente no mesmo grupo (RazaoSocial + UF)"
                })
            if grupo["Modalidade"].nunique() > 1:
                erros.append({
                    "CNPJ": grupo["CNPJ"].iloc[0],
                    "RazaoSocial": nome_grupo[0],
                    "Trimestre": grupo["Trimestre"].iloc[0],
                    "ValorDespesas": grupo["ValorDespesas"].sum(),
                    "TipoErro": "Modalidade diferente no mesmo grupo (RazaoSocial + UF)"
                })
            if grupo["RegistroANS"].nunique() > 1:
                erros.append({
                    "CNPJ": grupo["CNPJ"].iloc[0],
                    "RazaoSocial": nome_grupo[0],
                    "Trimestre": grupo["Trimestre"].iloc[0],
                    "ValorDespesas": grupo["ValorDespesas"].sum(),
                    "TipoErro": "RegistroANS diferente no mesmo grupo (RazaoSocial + UF)"
                })
    
    # Salva erros no Excel eliminando erros duplicados
    if erros:
        df_erros_novo = pd.DataFrame(erros).drop_duplicates()
        if df_erros_novo.empty:
            print("Nenhuma inconsistência encontrada nesta execução.")
        else:
            if os.path.exists(caminho_erros):
                try:
                    try:
                        df_erros_existente = pd.read_excel(caminho_erros, sheet_name="Erros", dtype=str)
                    except ValueError:
                        df_erros_existente = pd.DataFrame()
                
                    df_erros_final = pd.concat([df_erros_existente, df_erros_novo], ignore_index=True).drop_duplicates()
                    with pd.ExcelWriter(caminho_erros, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                        df_erros_final.to_excel(writer, index=False, sheet_name="Erros")                
                    novos = len(df_erros_final) - len(df_erros_existente)
                    print(f"{novos} novos erros adicionados. Total agora: {len(df_erros_final)}")
            
                except Exception as e:
                    print(f"Erro ao atualizar Excel existente: {e}")
                    print("→ Criando novo arquivo com os erros atuais.")
                    df_erros_novo.to_excel(caminho_erros, index=False, sheet_name="Erros")
            
            else:
                #Cria novo arquivo caso não exista
                df_erros_novo.to_excel(caminho_erros, index=False, sheet_name="Erros")
                print(f"{len(df_erros_novo)} inconsistências registradas (novo arquivo criado).")

    # Realiza o agrupamento desejado
    df_agrupado = df.groupby(
        ["RazaoSocial", "UF", "Modalidade", "RegistroANS", "CNPJ", "Status"],
        as_index=False,
        observed=True
    ).agg({
        "ValorDespesas": "sum",
        "Trimestre": lambda x: ", ".join(sorted(x.unique()))
    })

    # Mantém Status como última coluna
    cols = [col for col in df_agrupado.columns if col != "Status"] + ["Status"]
    df_agrupado = df_agrupado[cols]

    # Salva o novo arquivo
    df_agrupado.to_csv(caminho_novo, index=False, encoding="utf-8-sig")
    print(f"Agrupamento concluído!")

    #=====================#
    #Parte 2 - Média de Despesas e Erros Padrão
    #=====================#

    #Caminho dos arquivos a serem utilizados e criados
    caminho_agrupado = os.path.join(PASTA_RESULTADOS, "despesas_consolidadas_agrupado.csv")
    caminho_normalizados = os.path.join(PASTA_NORMALIZADOS, "dados_normalizados.csv")
    caminho_saida = os.path.join(PASTA_RESULTADOS, "despesas_agregadas.csv")

    #Verifica se arquivos existem 
    if not os.path.exists(caminho_agrupado):
        print("Arquivo despesas_consolidadas_agrupado.csv não encontrado.")
        return 
    if not os.path.exists(caminho_normalizados):
        print("Arquivo dados_normalizados.csv não encontrado.")
        return
    
    #Lê arquivos
    df_agrupado = pd.read_csv(caminho_agrupado, dtype=str)
    df_normal = pd.read_csv(caminho_normalizados, dtype={"registro_ans": str, "valor_inicial": float, "valor_final": float, "ano": int, "mes": int})

    #Cria a coluna de despesa calculada
    df_normal["Despesa"] = df_normal["valor_final"] - df_normal["valor_inicial"]

    #Calcula trimestre baseado no mês
    def calcular_trimestre(mes):
        if 1 <= mes <= 3:
            return "1º Trimestre"
        elif 4 <= mes <= 6:
            return "2º Trimestre"
        elif 7 <= mes <= 9:
            return "3º Trimestre"
        else:
            return "Outros"
    df_normal["Trimestre"] = df_normal["mes"].apply(calcular_trimestre)

    #Cria data frame com as colunas desejadas
    stats_por_trimestre = df_normal.groupby(["registro_ans", "Trimestre"]).agg({
        "Despesa": ["mean", "std"]
    }).reset_index()
    stats_por_trimestre.columns = ["registro_ans", "Trimestre", "Media_Despesa", "Desvio_Despesa"]

    #Pivot para colunas separadas por trimestre
    media_pivot = stats_por_trimestre.pivot(index="registro_ans", columns="Trimestre", values="Media_Despesa").reset_index()
    desvio_pivot = stats_por_trimestre.pivot(index="registro_ans", columns="Trimestre", values="Desvio_Despesa").reset_index()
    media_pivot.columns = ["registro_ans", "Media_1o_Trimestre", "Media_2o_Trimestre", "Media_3o_Trimestre"]
    desvio_pivot.columns = ["registro_ans", "Desvio_1o_Trimestre", "Desvio_2o_Trimestre", "Desvio_3o_Trimestre"]

    #Calcula média e desvio total por registro_ans
    stats_total = df_normal.groupby("registro_ans")["Despesa"].agg(["mean", "std"]).reset_index()
    stats_total.columns = ["registro_ans", "Media_Total", "Desvio_Total"]

    # Merge tudo no agrupado usando RegistroANS como chave
    df_agrupado = df_agrupado.merge(media_pivot, left_on="RegistroANS", right_on="registro_ans", how="left").drop(columns=["registro_ans"])
    df_agrupado = df_agrupado.merge(desvio_pivot, left_on="RegistroANS", right_on="registro_ans", how="left").drop(columns=["registro_ans"])
    df_agrupado = df_agrupado.merge(stats_total, left_on="RegistroANS", right_on="registro_ans", how="left").drop(columns=["registro_ans"])

    # Mantém Status como última coluna
    if "Status" in df_agrupado.columns:
        cols = [col for col in df_agrupado.columns if col != "Status"] + ["Status"]
        df_agrupado = df_agrupado[cols]
    
    #Converte colunas numéricas para float para ordenar corretamente
    numeric_cols = ["Media_1o_Trimestre", "Media_2o_Trimestre", "Media_3o_Trimestre", "Media_Total",
                    "Desvio_1o_Trimestre", "Desvio_2o_Trimestre", "Desvio_3o_Trimestre", "Desvio_Total"]
    for col in numeric_cols:
        if col in df_agrupado.columns:
            df_agrupado[col] = pd.to_numeric(df_agrupado[col], errors='coerce')
    
    #Ordena por Media_Total
    if "Media_Total" in df_agrupado.columns:
        df_agrupado = df_agrupado.sort_values(by="Media_Total", ascending=False).reset_index(drop=True)
    else:
        print("Coluna Media_Total não encontrada — ordenação não realizada.")

    # Salva como novo arquivo
    df_agrupado.to_csv(caminho_saida, index=False, encoding="utf-8-sig")
    print(f"Arquivo criado/atualizado: {caminho_saida}")