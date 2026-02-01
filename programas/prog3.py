import os
import mysql.connector
from programas.support_code import conectar_banco

#Caminhos das Pastas
BASE_DIR = "documents"
PASTA_DOWNLOADS = os.path.join(BASE_DIR, "downloads")
PASTA_EXTRAIDOS = os.path.join(BASE_DIR, "extraidos")
PASTA_NORMALIZADOS = os.path.join(BASE_DIR, "normalizados")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "resultados")

#Executa atividade 3
def executar():
    conn = None
    cursor = None
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
    
        #Busca os caminhos dos arquivos a serem usados
        caminho_consolidado = os.path.join(PASTA_RESULTADOS, "consolidado_despesas.csv")
        caminho_agregados = os.path.join(PASTA_RESULTADOS, "consolidado_despesas_erros.csv")

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    except mysql.connector.Error as err:
        print("Erro ao conectar:", err)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()