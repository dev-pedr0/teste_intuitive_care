from charset_normalizer import detect
import pandas as pd
import os

#Arquivo connversor de registro ans para cnpj e razão social
MAPA_REGISTRO = None

#Leitura correta de arquivo usando extensão e enconding correto
def ler_arquivo_com_encoding(caminho, max_bytes=200_000):
    
    #Leitura de arquivo excel
    if caminho.lower().endswith(".xlsx"):
        try:
            return pd.read_excel(caminho)
        except Exception as e:
            print(f"Erro ao ler XLSX {caminho}: {e}")
            return None

    #Leitura de arquivo .csv, .txt, .tsv. Detecção de encoding
    try:
        with open(caminho, 'rb') as f:
            raw = f.read(max_bytes)  # lê só o início para detecção rápida

        #Busca detectar o encondig e porcentagem de certeza
        resultado = detect(raw)
        encoding = resultado['encoding']
        confianca = resultado['confidence']

        #Em caso de incerteza do encondig usa uft-8
        if encoding is None or confianca < 0.5:
            print(f"Detecção fraca para {caminho} (confiança {confianca:.0%}) → usando fallback latin-1")
            encoding = "utf-8"

        print(f"[{os.path.basename(caminho)}] Encoding detectado: {encoding} (confiança: {confianca:.0%})")

        #Gera um dataframe com o encondig e formato de arquivo
        df = pd.read_csv(
            caminho,
            encoding=encoding,
            sep=None,
            engine="python",
            on_bad_lines="skip",       # ignora linhas problemáticas
            encoding_errors="replace"  # substitui caracteres inválidos
        )
        return df

    #Lida com erros
    except UnicodeDecodeError:
        print(f"Falha com {encoding} em {caminho} → tentando utf-8-sig fallback")
        try:
            return pd.read_csv(caminho, encoding="utf-8-sig", sep=None, engine="python")
        except Exception as e:
            print(f"Fallback também falhou: {e}")
            return None
    except Exception as e:
        print(f"Erro geral ao ler {caminho}: {e}")
        return None

#Calcula o trimestre baseado no número do mês    
def calcular_trimestre(mes):
        if mes in [1, 2, 3]:
            return "1º Trimestre"
        elif mes in [4, 5, 6]:
            return "2º Trimestre"
        elif mes in [7, 8, 9]:
            return "3º Trimestre"
        elif mes in [10, 11, 12]:
            return "4º Trimestre"
        else:
            return None

#Carrega o conversor para evitar multiplos carregamentos
def carregar_mapa_conversor():
    global MAPA_REGISTRO

    if MAPA_REGISTRO is not None:
        return MAPA_REGISTRO

    caminho = os.path.join("documents", "resultados", "mapa_registro_ans_cnpj.csv")

    if not os.path.exists(caminho):
        print("Arquivo mapa_registro_ans_cnpj.csv não encontrado.")
        return None

    df = pd.read_csv(caminho, dtype=str)

    MAPA_REGISTRO = df.set_index("registro_ans")[["cnpj", "razao_social"]]


#Conversor registro ans para razão social e cnpj
def buscar_cnpj_razao(registro_ans):

    #Busca a variável global do conversor
    mapa = carregar_mapa_conversor()

    if mapa is None:
        return None, None

    #Trasforma o registro em texto
    registro_ans = str(registro_ans)

    if registro_ans not in mapa.index:
        return None, None
    
    #Localiza a linha do registro
    linha = mapa.loc[registro_ans]

    #Retorna cnpj e razão cosial de acordo com registro
    return linha["cnpj"], linha["razao_social"]


#Validador de CNPJ
def cnpj_valido(cnpj: str) -> bool:
    if not cnpj:
        return False
    
    #Remove caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, cnpj))

    #Deve ter 14 dígitos
    if len(cnpj) != 14:
        return False
    
    #Rejeita CNPJs com todos os dígitos iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    #Calculo de validação de cnpj por pesos
    def calcular_digito(cnpj_base, pesos):
        soma = sum(int(d) * p for d, p in zip(cnpj_base, pesos))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)
    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6] + pesos_1
    digito_1 = calcular_digito(cnpj[:12], pesos_1)
    digito_2 = calcular_digito(cnpj[:13], pesos_2)
    return cnpj[-2:] == digito_1 + digito_2


#Função de registro de erros
def registrar_erros(erros, caminho_erros):
    if not erros:
        return
    
    #Cria colunas padronizadas
    colunas_fixas = [
        "TipoErro", "CNPJ", "RazaoSocial", "CNPJsDiferentes",
        "Quantidade", "QuantidadeLinhasAfetadas", "LinhasAfetadas", "Detalhes"
    ]

    #Gera data frame de erros
    df_erros_novos = pd.DataFrame(erros)

    #Gera todas as colunas
    for col in colunas_fixas:
        if col not in df_erros_novos.columns:
            df_erros_novos[col] = ""
    df_erros_novos = df_erros_novos[colunas_fixas].fillna("")

    # Se arquivo não existir, cria
    if not os.path.exists(caminho_erros):
        df_erros_novos.to_csv(
            caminho_erros,
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )
        print(f"Arquivo de erros criado: {caminho_erros}")
        print(f"{len(df_erros_novos)} erro(s) registrado(s).")
        return
    
    #Acessa arquivo
    try:
        df_erros_existentes = pd.read_csv(caminho_erros, sep=";", dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        # Caso raro: tem tamanho >0 mas pandas não lê (ex: só espaços), sobrescreve o arquivo
        print("Arquivo existente parece vazio ou corrompido → sobrescrevendo.")
        df_erros_novos.to_csv(caminho_erros, sep=";", index=False, encoding="utf-8-sig")
        return
    except Exception as e:
        print(f"Erro inesperado ao ler arquivo de erros: {e}")
        return

    # Concatena os erros existentes e novos
    df_final = pd.concat([df_erros_existentes, df_erros_novos], ignore_index=True).fillna("")

    # Remove duplicatas considerando TODAS as colunas
    df_final = df_final.drop_duplicates()

    novos = len(df_final) - len(df_erros_existentes)
    
    if novos > 0:
        df_final.to_csv(
            caminho_erros,
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )
        print(f"{novos} erro(s) novo(s) adicionado(s) em {caminho_erros}")
    else:
        print("Nenhum erro novo para adicionar.")