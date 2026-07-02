# src/schemas/ponto.py
from datetime import datetime, date
from pydantic import BaseModel
from typing import List, Optional
from src.core.ponto import PontosBatidos  

class RegistroPontoCreate(BaseModel):
    usuario_id: int
    observacao: Optional[str] = None


class RegistroPontoResponse(BaseModel):
    id: int
    id_jornada: int
    horario: datetime
    registro: PontosBatidos

    class Config:
        from_attributes = True


class JornadaDiariaResponse(BaseModel):
    id: int
    id_user: int
    data: date
    status: bool
    saldo_horas: int
    pontos: List[RegistroPontoResponse] = []  # Relacionamento automático

    class Config:
        from_attributes = True

class RegistroPontoUpdate(BaseModel):
    horario: datetime

    class Config:
        from_attributes = True
