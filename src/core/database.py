
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Caminho do seu banco SQLite local
SQLALCHEMY_DATABASE_URL = "sqlite:///./cronosflow.db"

# A engine é quem gerencia a conexão física com o arquivo .db
# O "check_same_thread=False" é obrigatório apenas para o SQLite no FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Essa é a fábrica que vai gerar as sessões (SessionLocal) para as nossas rotas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A sua classe base que o Alembic e os modelos já usam
class Base(DeclarativeBase):
    pass