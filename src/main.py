
from fastapi import FastAPI
from contextlib import asynccontextmanager



app = FastAPI(
    title="CronosFlow - Ponto e Banco de Horas",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "produto": "Anti-Caos Ponto",
        "mensagem": "Bora vencer o caos do banco de horas, Padrinho!"
    }