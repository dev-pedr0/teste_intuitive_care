import csv
import os
import re
import time
import zipfile
import requests
import pandas as pd
from bs4 import BeautifulSoup
from programas.support_code import buscar_cnpj_razao, calcular_trimestre, ler_arquivo_com_encoding

#Caminhos das Pastas
BASE_DIR = "documents"
PASTA_DOWNLOADS = os.path.join(BASE_DIR, "downloads")
PASTA_EXTRAIDOS = os.path.join(BASE_DIR, "extraidos")
PASTA_NORMALIZADOS = os.path.join(BASE_DIR, "normalizados")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "resultados")

#Caminho para extração de arquivos trimestrais
ARQUIVOS_ESPERADOS = []

# Cria todas as pastas de uma vez
os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
os.makedirs(PASTA_EXTRAIDOS, exist_ok=True)
os.makedirs(PASTA_NORMALIZADOS, exist_ok=True)
os.makedirs(PASTA_RESULTADOS, exist_ok=True)

#Menu da atividade 1
def executar():
    while True:
        print("\n=== Atividade 1 ===")
        print("1 - Item 1.1")
        print("2 - Item 1.2")
        print("3 - Item 1.3")
        print("4 - Executar todos")
        print("0 - Sair")
        opcao = input("Escolha: ")

        match opcao:
            case "1":
                print("Iniciando item 1.1")
                atividade11()
            case "2":
                print("Iniciando item 1.2")
                atividade12()
            case "3":
                print("Iniciando item 1.3")
                atividade13()
            case "4":
                print("Iniciando item 1.1")
                atividade11()
                print("Iniciando item 1.2")
                atividade12()
                print("Iniciando item 1.3")
                atividade13()
            case "0":
                print("Fechando atividade 1")
                break
            case _:
                print("Valor inválido")

#Atividade 1.1
def atividade11():
    global ARQUIVOS_ESPERADOS

    print("Extração dos 3 ultimos trimestres:")

    #Acessa a API
    url = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
    resposta = requests.get(url)

    #Para a execução em caso de erro no retorno da API
    if resposta.status_code != 200:
        print("Erro ao acessar página principal")
        return
    
    #Em caso de acesso a API busca todos os links dentro da mesma
    soup = BeautifulSoup(resposta.text, "html.parser")
    anchors = soup.find_all("a")
    links = []
    for a in anchors:
        href = a.get("href")
        if href:
            links.append(href)
    
    #Filtra os links que são anos e os ordena
    anos = []
    for link in links:
        if re.match(r"^\d{4}/$", link):
            anos.append(link)
    anos=sorted(anos, reverse=True)

    #Array onde salvos os nomes dos arquivos
    arquivos = []

    #Busca pelos ultimos 3 arquivos
    for ano in anos:
        #Verifica se já foram identificados 3 arquivos para interromper o for
        if len(arquivos) >= 3:
            break
        
        #Acessa a url de cada ano e busca links com texto .zip
        url_ano = url + ano
        resp_ano = requests.get(url_ano)

        #Para a execução em caso de erro no retorno da API 
        if resposta.status_code != 200:
            print("Erro ao acessar página principal")
            return

        #Busca todos os links válidos
        soup_ano = BeautifulSoup(resp_ano.text, "html.parser")
        anchors = soup_ano.find_all("a")
        hrefs = []
        for a in anchors:
            href = a.get("href")
            if href:
                hrefs.append(href)

        ano_puro = ano.rstrip("/")

        # Filtro para variações de nomes trimestrais
        padroes_trimestre = [
            rf"^[1-4]T{re.escape(ano_puro)}\.zip$",  # Padrão novo: 1T2025.zip
            rf"^{re.escape(ano_puro)}_[1-4]_trimestre\.zip$",  # Padrão antigo: 2025_1_trimestre.zip
            rf"^[1-4](?:_trimestre|o_trimestre|º_trimestre|ºT)\.zip$",  # Variações como 1_trimestre, 1º_trimestre, 1ºT
            rf"^primeiro|segundo|terceiro|quarto_trimestre_{re.escape(ano_puro)}\.zip$"  # Extenso: primeiro_trimestre_2025.zip
        ]

        #Adiciona o link de cada documento válido
        arquivos_ano = []
        for href in hrefs:
            #Verifica se é um arquivo zip
            if not href.lower().endswith(".zip"):
                continue

            #Testa os filtros para encontrar arquivos de trimestres  
            nome_arquivo = href.lower()
            corresponde_a_padrao = False
            for padrao in padroes_trimestre:
                #Filtro aceito - documento adicionado
                if re.match(padrao, href, re.IGNORECASE):
                    corresponde_a_padrao = True
                    break    
            if corresponde_a_padrao:
                url_completa = url_ano + href
                if href not in ARQUIVOS_ESPERADOS:
                    ARQUIVOS_ESPERADOS.append( url_completa)
                arquivos_ano.append(url_ano + href)


        #Ordena dos arquivos mais novos para os mais antigos
        arquivos_ano.sort(reverse=True)

        #Envia para a variavel arquivo um arquivo por vez até um máximo de 3
        for arquivo in arquivos_ano:
            if len(arquivos) < 3:
                arquivos.append(arquivo)
            else:
                break

    #Acessa as urls em arquivos e baixa cada arquivo
    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
    for url in arquivos:
        #Salva nome do arquivo e caminho onde será salvo
        nome_arquivo = url.split("/")[-1]
        caminho = os.path.join(PASTA_DOWNLOADS, nome_arquivo)
        
        #Verifica se arquivo já existe
        if os.path.exists(caminho):
            print(f"Arquivo já existe: {nome_arquivo}")
            continue
        
        #Tenta baixar e escrever cada arquivo na pasta downloads
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(caminho, "wb") as f:
                f.write(r.content)            
            print("Arquivo baixado com sucesso")
        
        except requests.exceptions.RequestException as e:
            print(f"FALHA - {str(e)}")
        
        except Exception as e:
            print(f"ERRO INESPERADO - {str(e)}")

#Atividade 1.2
def atividade12():
    #Verifica se existem caminhos para baixar os arquivos trimestrais
    if not ARQUIVOS_ESPERADOS:
        print("Nenhum arquivo esperado registrado. Execute atividade11() primeiro.")
        return
    
    #Acessa a pasta downloads e verifica se os arquivos trimestrais existem
    os.makedirs(PASTA_DOWNLOADS, exist_ok=True)
    for url in ARQUIVOS_ESPERADOS: 
        nome_arquivo = url.split("/")[-1]
        caminho = os.path.join(PASTA_DOWNLOADS, nome_arquivo)
        #Se existir o arquivo o código segue
        if os.path.exists(caminho):
            continue
    
        #Se o arquivo não existir ele é baixado
        print(f"Arquivo não encontrado localmente. Iniciando download: {nome_arquivo}")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()        
            with open(caminho, "wb") as f:
                f.write(r.content)       
            print(f"Download concluído com sucesso: {nome_arquivo}") 

        except requests.exceptions.RequestException as e:
            print(f"Falha no download de {nome_arquivo}: {str(e)}") 

        except Exception as e:
            print(f"Erro inesperado ao processar {nome_arquivo}: {str(e)}")

    #Variável que guarda as linhas desejadas
    linhas_normalizadas = []

    #Extração de arquivos .zip
    for nome_zip in os.listdir(PASTA_DOWNLOADS):
       
        #Busca apenas por arquivos .zip
        if not nome_zip.endswith(".zip"):
            continue

        #Identifica o caminho de cada arquivo e seu nome
        caminho_zip = os.path.join(PASTA_DOWNLOADS, nome_zip)

        with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
            
            #Extrai todos os arquivos
            zip_ref.extractall(PASTA_EXTRAIDOS)

            #Lista todos os arquivos extraidos
            arquivos_extraidos = []
            for nome in zip_ref.namelist():
                if not nome.endswith('/'):
                    caminho = os.path.join(PASTA_EXTRAIDOS, nome)
                    arquivos_extraidos.append(caminho)

            #Filtro de busca pelo arquivo desejado padrão XTYYY (X=1-4)
            arquivos_alvo = [
                caminho for caminho in arquivos_extraidos
                if re.match(r"^[1-4]T\d{4}\.\w+$", os.path.basename(caminho))
            ]
            if not arquivos_alvo:
                print(f"Nenhum arquivo no padrão XTYYYY encontrado em {caminho_zip}")
                continue
            
            for caminho_extraido in arquivos_alvo:
                # Leitura do arquivo verificando extensão e encoding através de função auxiliar
                try:
                    documento = ler_arquivo_com_encoding(caminho_extraido)                   
                    if documento is not None:
                        print(f"Arquivo processado com sucesso: {caminho_extraido}")
                                                
                        df = documento
                        
                        # Identifica colunas que contêm texto
                        colunas_textuais = [
                            col for col in df.columns
                            if df[col].dtype == 'object' or not pd.api.types.is_numeric_dtype(df[col])
                        ]
                        if not colunas_textuais:
                            print(f"Nenhuma coluna textual encontrada em: {caminho_extraido}")
                            continue
                        
                        # Busca o texto exato "Despesas com Eventos / Sinistros" em qualquer coluna textual
                        if 'DESCRICAO' in df.columns:
                            col_desc = 'DESCRICAO'
                        elif len(df.columns) > 3:
                            col_desc = df.columns[3]
                        else:
                            col_desc = colunas_textuais[0] if colunas_textuais else None

                        if col_desc:
                            filtro = (df[col_desc].astype(str).str.strip() == "Despesas com Eventos / Sinistros")
                        else:
                            filtro = pd.Series(False, index=df.index)
                        if not filtro.any() and len(colunas_textuais) > 1:
                            filtro = pd.Series(False, index=df.index)
                            for col in colunas_textuais:
                                filtro |= (df[col].astype(str).str.strip() == "Despesas com Eventos / Sinistros")
                        linhas_filtradas = df[filtro]

                        # Adiciona linhas filtradas em linhas_normalizadas
                        if not linhas_filtradas.empty:
                            linhas_normalizadas.append(linhas_filtradas)
                            print(f"Linhas adicionadas com sucesso: {caminho_extraido}")
                        else:
                            print(f"Nenhuma linha correspondente a 'Despesas com Eventos / Sinistros' encontrada")
                    else:
                        print(f"Não foi possível ler o arquivo: {caminho_extraido}")
                
                except Exception as e:
                    print(f"Erro inesperado ao processar {caminho_extraido}: {e}")
    
    #Criação de novo arquivo com as linhas desejadas
    if linhas_normalizadas:
        resultado_final = pd.concat(linhas_normalizadas, ignore_index=True)

        #Renome de colunas para melhor entendimento
        mapa_colunas = {
            "DATA": "data_referencia",
            "REG_ANS": "registro_ans",
            "CD_CONTA_CONTABIL": "conta_contabil",
            "DESCRICAO": "tipo_despesa",
            "VL_SALDO_INICIAL": "valor_inicial",
            "VL_SALDO_FINAL": "valor_final"
        }
        resultado_final = resultado_final.rename(columns={
            col: mapa_colunas[col]
            for col in resultado_final.columns
            if col in mapa_colunas
        })

        # Normalizar valores numéricos
        if "valor_inicial" in resultado_final.columns:
            resultado_final["valor_inicial"] = (
                resultado_final["valor_inicial"]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype(float)
            )

        if "valor_final" in resultado_final.columns:
            resultado_final["valor_final"] = (
                resultado_final["valor_final"]
                .astype(str)
                .str.replace(",", ".", regex=False)
                .astype(float)
            )

        # Normalizar texto da descrição
        if "tipo_despesa" in resultado_final.columns:
            resultado_final["tipo_despesa"] = resultado_final["tipo_despesa"].str.lower()

        # Criar colunas derivadas
        if "data_referencia" in resultado_final.columns:
            datas = pd.to_datetime(resultado_final["data_referencia"], errors="coerce")
            resultado_final["ano"] = datas.dt.year
            resultado_final["mes"] = datas.dt.month

        # Cria o documento final normalizado
        caminho_saida = os.path.join(PASTA_NORMALIZADOS, "dados_normalizados.csv")
        resultado_final.to_csv(caminho_saida, index=False)
        print(f"\nArquivo normalizado criado: {caminho_saida}")
    else:
        print("\nNenhuma linha encontrada para normalização.")    

#Atividade 1.3
def atividade13():
    #=====================#
    #Parte 1 - criar conversor de registro ans para cnpj e razão social
    #=====================#
    
    #Url dos documentos que convertem registro ans para cnpj e razão social
    BASE_URLS = [
        "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/",
        "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_canceladas/"
    ]
    
    registros = []
    
    for base_url in BASE_URLS:
        print(f"Acessando: {base_url}")
        html = requests.get(base_url).text
        soup = BeautifulSoup(html, "html.parser")

        #Procurar arquivo que contenha "relatorio_cadop"
        arquivos = [a.get("href") for a in soup.find_all("a")]
        alvo = None
        for nome in arquivos:
            if nome and re.search(r"relatorio.*cadop", nome, re.IGNORECASE):
                alvo = nome
                break

        if not alvo:
            print("Arquivo relatorio_cadop não encontrado.")
            continue
        
        #Baixa o arquivo buscado na pasta downloads
        url_arquivo = base_url + alvo
        print(f"Arquivo encontrado: {url_arquivo}")
        nome_arquivo = alvo
        caminho_arquivo = os.path.join(PASTA_DOWNLOADS, nome_arquivo)
        resposta = requests.get(url_arquivo)
        with open(caminho_arquivo, "wb") as f:
            f.write(resposta.content)
        print(f"Arquivo baixado: {caminho_arquivo}")

        #Lê o arquivo corretamente com extensão e enconding correto
        df = ler_arquivo_com_encoding(caminho_arquivo)
        if df is None:
            print(f"Não foi possível ler o arquivo: {caminho_arquivo}")
            continue
        
        #Normalização do texto das colunas
        colunas = {c.upper(): c for c in df.columns}
        
        #Busca colunas desejadas
        def achar_coluna(possiveis):
            for p in possiveis:
                for c in colunas:
                    if p in c:
                        return colunas[c]
            return None
        col_registro = achar_coluna(["REGISTRO"])
        col_cnpj = achar_coluna(["CNPJ"])
        col_razao = achar_coluna(["RAZAO", "RAZÃO", "RAZAO_SOCIAL", "RAZÃO_SOCIAL"])

        if not (col_registro and col_cnpj and col_razao):
            print("Colunas necessárias não encontradas.")
            continue

        #Copia as colunas desejadas
        df_final = df[[col_registro, col_cnpj, col_razao]].copy()
        df_final.columns = ["registro_ans", "cnpj", "razao_social"]
        #Cria coluna para verificar se é registro ativo ou cancelado
        status = "ativo" if "ativas" in base_url else "cancelado"
        df_final["status"] = status
        registros.append(df_final)
    
        if not registros:
            print("Nenhum dado encontrado para criar arquivo chave")
            return
        
        #Concatena tudo
        resultado = pd.concat(registros, ignore_index=True)

        #Busca detectar cnpj's duplicados
        duplicados = resultado.groupby("cnpj").size() > 1
        if duplicados.any():
            erros = []
            for cnpj_duplicado in resultado[resultado["cnpj"].duplicated(keep=False)]["cnpj"].unique():
                grupo = resultado[resultado["cnpj"] == cnpj_duplicado]

                #Remove duplicada de registro cancelado
                if "ativo" in grupo["status"].values and "cancelado" in grupo["status"].values:
                    resultado = resultado.drop(grupo[grupo["status"] == "cancelado"].index)

                #Gera log de erro para verificação se forem duplicatas ativas
                elif all(grupo["status"] == "ativo"):
                    razoes = " / ".join(grupo["razao_social"].unique())
                    registros_ans = ", ".join(grupo["registro_ans"].astype(str).unique())
                    erros.append({
                        "CNPJ": cnpj_duplicado,
                        "RazoesConflitantes": razoes,
                        "RegistrosANS": registros_ans,
                        "TipoErro": "Duplicado em ativos"
                    })

                    #Cria flag nas linhas que tem duplicatas
                    linha_mantida = grupo.iloc[0].copy()
                    linha_mantida["razao_social"] = f"[DUPLICADO ATIVO] {razoes}"
                    resultado = resultado.drop(grupo.index)
                    resultado = pd.concat([resultado, linha_mantida.to_frame().T], ignore_index=True)
                    print(f"Duplicado em ativos flagado: {cnpj_duplicado}")

        #Salva o mapa conversor
        caminho_saida = os.path.join(PASTA_RESULTADOS, "mapa_registro_ans_cnpj.csv")
        resultado.to_csv(caminho_saida, index=False)
        print(f"\nArquivo criado: {caminho_saida}")

    #=====================#
    #Parte 2 - criar arquivo de despesas gerais
    #=====================#

    #salva o caminho do arquivo a ser utilizado
    caminho_arquivo = os.path.join(PASTA_NORMALIZADOS, "dados_normalizados.csv")
    
    #Verifica se o arquivo existe
    if not os.path.exists(caminho_arquivo):
        print("Arquivo dados_normalizados.csv não encontrado.")
        return
    
    #Lê o arquivo
    df = pd.read_csv(caminho_arquivo)

    #Busca o cnpj e razão sociual baseado no registro ans
    cnpj_razao = df["registro_ans"].apply(buscar_cnpj_razao)

    #Criação das colunas do novo arquivo
    df["CNPJ"] = cnpj_razao.apply(
        lambda x: x[0] if x is not None else f"não encontrado/{x.name}"
    )

    df["RazaoSocial"] = cnpj_razao.apply(
        lambda x: x[1] if x is not None else f"não encontrado/{x.name}"
    )
    df["Ano"] = df["ano"]
    df["Trimestre"] = df["mes"].apply(calcular_trimestre)
    df["ValorDespesas"] = df["valor_final"] - df["valor_inicial"]

    colunas_finais = ["CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"]
    df_final = df[colunas_finais]

    #=====================#
    #Parte 3 - Verificar erros
    #=====================#
    erros_cnpj_razao = []
    erros_valores = []
    erros_padronizados = []

    #Verifica CNPJs com mais de uma Razão Social
    cnpj_multi_razao = df_final.groupby("CNPJ")["RazaoSocial"].nunique() > 1
    cnpjs_problematicos = cnpj_multi_razao[cnpj_multi_razao].index

    #Registra o erro
    for cnpj in cnpjs_problematicos:
        grupo = df_final[df_final["CNPJ"] == cnpj]
        razoes_unicas = grupo["RazaoSocial"].unique()
        razoes_str = " | ".join(razoes_unicas)
        linhas_afetadas = grupo.index.tolist()
        
        erros_cnpj_razao.append({
            "TipoErro": "CNPJ com múltiplas Razões Sociais",
            "CNPJ": cnpj,
            "RazoesSociaisDiferentes": razoes_str,
            "QuantidadeRazoes": len(razoes_unicas),
            "QuantidadeLinhasAfetadas": len(grupo),
            "LinhasAfetadas": ", ".join(map(str, linhas_afetadas))
        })
    
    #Verifica Razões Sociais com mais de um CNPJ
    razao_multi_cnpj = df_final.groupby("RazaoSocial")["CNPJ"].nunique() > 1
    razoes_problematicas = razao_multi_cnpj[razao_multi_cnpj].index
    for razao in razoes_problematicas:
        grupo = df_final[df_final["RazaoSocial"] == razao]
        cnpjs_unicos = grupo["CNPJ"].unique()
        cnpjs_str = " | ".join(cnpjs_unicos)
        linhas_afetadas = grupo.index.tolist()
        
        erros_cnpj_razao.append({
            "TipoErro": "Razão Social com múltiplos CNPJs",
            "RazaoSocial": razao,
            "CNPJsDiferentes": cnpjs_str,
            "QuantidadeCNPJs": len(cnpjs_unicos),
            "QuantidadeLinhasAfetadas": len(grupo),
            "LinhasAfetadas": ", ".join(map(str, linhas_afetadas))
        })

    #Verifica valores zerados e negativos
    zerados = df_final[df_final["ValorDespesas"] == 0]
    if not zerados.empty:
        zerados_log = zerados.copy()
        zerados_log["TipoErro"] = "ValorDespesas zerado"
        erros_valores.append(zerados_log)
        
        # Remove zerados
        df_final = df_final[df_final["ValorDespesas"] != 0]

    negativos = df_final[df_final["ValorDespesas"] < 0]
    if not negativos.empty:
        negativos_log = negativos.copy()
        negativos_log["TipoErro"] = "ValorDespesas negativo"
        erros_valores.append(negativos_log)

    #Padronização dos erros
    for erro in erros_cnpj_razao:
        erros_padronizados.append({
            "TipoErro": erro["TipoErro"],
            "CNPJ": erro.get("CNPJ", ""),
            "RazaoSocial": erro.get("RazaoSocial", ""),
            "CNPJsDiferentes": erro.get("CNPJsDiferentes", erro.get("RazoesSociaisDiferentes", "")),
            "Quantidade": erro.get("QuantidadeCNPJs", erro.get("QuantidadeRazoes", "")),
            "QuantidadeLinhasAfetadas": erro.get("QuantidadeLinhasAfetadas", ""),
            "LinhasAfetadas": erro.get("LinhasAfetadas", ""),
            "Detalhes": ""  # campo extra para valores zerados/negativos
        })
    if erros_valores:
        df_valores = pd.concat(erros_valores, ignore_index=True)
        for _, row in df_valores.iterrows():
            erros_padronizados.append({
                "TipoErro": row["TipoErro"],
                "CNPJ": row.get("CNPJ", ""),
                "RazaoSocial": row.get("RazaoSocial", ""),
                "CNPJsDiferentes": "",
                "Quantidade": "",
                "QuantidadeLinhasAfetadas": "",
                "LinhasAfetadas": "",
                "Detalhes": f"Trimestre: {row.get('Trimestre', '')} | Ano: {row.get('Ano', '')} | ValorDespesas: {row.get('ValorDespesas', '')}"
            })

    #Criação/Atualização de arquivo de erro
    if erros_padronizados:
        df_erros = pd.DataFrame(erros_padronizados)
        
        # Colunas fixas e ordenadas
        colunas_fixas = [
            "TipoErro", "CNPJ", "RazaoSocial", "CNPJsDiferentes",
            "Quantidade", "QuantidadeLinhasAfetadas", "LinhasAfetadas", "Detalhes"
        ]
        
        # Verifica se arquivo existe para decidir se escreve cabeçalho
        caminho_erros = os.path.join(PASTA_RESULTADOS, "consolidado_despesas_erros.csv")
        arquivo_existe = os.path.exists(caminho_erros)
        df_erros[colunas_fixas].to_csv(
            caminho_erros,
            mode='a',                      # adiciona ao final
            header=not arquivo_existe,     # cabeçalho só na primeira vez
            index=False,
            encoding='utf-8-sig',
            sep=';',
            quoting=csv.QUOTE_MINIMAL
        )
        print(f"Erros adicionados em: {caminho_erros}")
        print(f"Total de erros registrados nesta execução: {len(erros_padronizados)}")
    else:
        print("Nenhuma inconsistência ou valor suspeito encontrado.")

    #Criação do arquivo de despesas
    caminho_saida = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.csv")
    df_final.to_csv(caminho_saida, index=False)
    print(f"Arquivo criado com sucesso: {caminho_saida}")

    #Compactação do arquivo em um .zip
    caminho_csv = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.csv")
    caminho_zip = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.zip")
    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(caminho_csv, arcname="consolidado_despesas.csv")
    print(f"Arquivo ZIP criado: {caminho_zip}")