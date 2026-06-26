
from datetime import datetime, date
from pydantic import BaseModel
from typing import List, Optional

from src.core.ponto import PontosBatidos


class RegistroPontoCreate(BaseModel):
    """
    O que a API precisa receber quando o usuário clica em 'Bater Ponto'.
    Não precisamos enviar o horário, pois o backend usará o relógio do servidor
    para evitar que o usuário altere a hora do ponto!
    """
    usuario_id: int
    observacao: Optional[str] = None


class RegistroPontoResponse(BaseModel):
    """
    O que a API devolve ao front-end após o ponto ser registrado com sucesso.
    """
    id: int
    jornada_id: int
    horario: datetime
    tipo_ponto: PontosBatidos
    observacao: Optional[str]

    class Config:
        from_attributes = True



class JornadaDiariaResponse(BaseModel):
    """
    Representa o dia de trabalho completo do funcionário,
    mostrando todos os pontos que ele bateu naquele dia específico.
    """
    id: int
    usuario_id: int
    data: date
    horas_trabalhadas: float = 0.0
    fechada: bool
    
    
    pontos: List[RegistroPontoResponse] = []

    class Config:
        from_attributes = True