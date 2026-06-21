from sqlalchemy import Column, Integer, String, Float, Boolean, Enum
import enum
from src.core.database import Base


class RegimeTrabalho(str, enum.Enum):
    CLT = "CLT"
    PJ = "PJ"
    ESTAGIO = "ESTAGIO"
    AUTONOMO = "AUTONOMO"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    #configurando a jornada de trabalho
    regime = Column(Enum(RegimeTrabalho), default=RegimeTrabalho.CLT, nullable=False)

    #carga horária em minutos para facilitar os calculos, 8h = 480 minutos
    carga_horaria_diaria = Column(Integer, default=480, nullable=False)

    #valor recido por hora
    valor_hora = Column(Float, default=0.0, nullable=False)