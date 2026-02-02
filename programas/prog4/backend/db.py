import os
from dotenv import load_dotenv
import mysql.connector

#Roda o .env
load_dotenv() 

#Conecta ao banco de dados MySQL
def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connection_timeout=5
    )