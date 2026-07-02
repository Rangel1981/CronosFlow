from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.schemas.ponto import JornadaDiariaResponse, RegistroPontoCreate, RegistroPontoResponse, RegistroPontoUpdate
from src.repositories.ponto_repository import PontoRepository
from src.core.database import SessionLocal  
from src.schemas.user import UserCreate, UserResponse
from src.repositories.user_repository import UserRepository

app = FastAPI(title="CronosFlow API", version="0.1.0", summary="Um produto criado por Arthur Rangel!")

#dependência para gerenciar a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função temporária de criptografia 
def fake_hash_password(password: str) -> str:
    return password + "fake_hash"


#rota de Cadastro de Usuário
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint para cadastrar um novo trabalhador no sistema.
    """
    # Inicializa o repositório passando a sessão do banco
    user_repo = UserRepository(db)
    
    # Regra de Negócio: Verifica se o e-mail já está cadastrado
    usuario_existente = user_repo.get_by_email(user_in.email)
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado no sistema."
        )
    
    # Criptografa a senha temporaria
    senha_criptografada = fake_hash_password(user_in.password)
    
    # Salva no banco de dados usando o repositório
    novo_usuario = user_repo.create(user_in, hashed_password=senha_criptografada)
    
    return novo_usuario

@app.get("/")
def read_root():
    return {"message": "CronosFlow rodando liso!"}


@app.post("/pontos", response_model=RegistroPontoResponse, status_code=status.HTTP_201_CREATED)
def bater_ponto(ponto_in: RegistroPontoCreate, db: Session = Depends(get_db)):
    """
    Endpoint para o trabalhador registrar o ponto (Entrada, Almoço, Saída).
    A jornada é controlada e criada automaticamente se for o primeiro ponto do dia.
    """
    #iniciando repositorio de ponto e passando para a sessão de ponto para o banco
    ponto_repo = PontoRepository(db)

    novo_registro = ponto_repo.bater_ponto(ponto_in)

    return novo_registro

@app.get("/pontos/{user_id}", response_model=List[JornadaDiariaResponse]) 
def listar_pontos(user_id: int, db: Session = Depends(get_db)):
    ponto_repo = PontoRepository(db)
    registros = ponto_repo.listar_pontos_por_usuario(user_id)
    return registros

@app.put("/ponto/{ponto_id}", response_model=RegistroPontoResponse)
def editar_registro_ponto(ponto_id: int, ponto_in: RegistroPontoUpdate, db: Session = Depends(get_db)):
    ponto_repo = PontoRepository(db)
    ponto_atualizado = ponto_repo.atualizar_ponto(ponto_id, ponto_in)
    return ponto_atualizado