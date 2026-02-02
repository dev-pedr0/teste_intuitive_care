from fastapi import FastAPI
from db import conectar_banco

app = FastAPI(title="API Operadoras de Saúde")

@app.get("/db-test")
def testar_banco():
    try:
        conn = conectar_banco()
        conn.close()
        return {"status": "conectado com sucesso"}
    except Exception as e:
        return {"erro": str(e)}