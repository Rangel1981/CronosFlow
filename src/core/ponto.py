
from sqlalchemy import Column, Integer, Boolean, Enum, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
import enum
from src.core.database import Base

class PontosBatidos(str, enum.Enum):
    ENTRADA = "ENTRADA"
    ALMOCO_SAIDA = "ALMOCO_SAIDA"
    ALMOCO_ENTRADA = "ALMOCO_ENTRADA"
    SAIDA = "SAIDA"

class JornadaDiaria(Base):
    __tablename__ = "jornadas_diarias"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(Boolean, default=True) # True = Aberta, False = Fechada
    saldo_horas = Column(Integer, default=0) # Saldo em minutos
    data = Column(Date, nullable=False) 

    # Relacionamento para conseguir fazer: jornada.pontos (puxar todas as batidas do dia)
    pontos = relationship("RegistroPonto", back_populates="jornada", cascade="all, delete-orphan")

class RegistroPonto(Base):
    __tablename__ = "registros_pontos"

    id = Column(Integer, primary_key=True, index=True)
    id_jornada = Column(Integer, ForeignKey("jornadas_diarias.id"), index=True)
    horario = Column(DateTime(timezone=True), nullable=False) # Hora exata com fuso
    registro = Column(Enum(PontosBatidos), default=PontosBatidos.ENTRADA, nullable=False)

    #relacionamento inverso, saber qual dia o ponto foi batido
    jornada = relationship("JornadaDiaria", back_populates="pontos")