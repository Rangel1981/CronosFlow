# src/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session


from src.core.database import SessionLocal  # Garanta que você tem a SessionLocal criada lá
from src.schemas.user import UserCreate, UserResponse
from src.repositories.user_repository import UserRepository

app = FastAPI(title="CronosFlow API", version="0.1.0", summary="Um produto criado por Arthur Rangel!")

# 1. Dependência para gerenciar a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função temporária de criptografia (vamos evoluir isso logo mais!)
def fake_hash_password(password: str) -> str:
    return password + "fake_hash"


# 2. A Rota de Cadastro de Usuário
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