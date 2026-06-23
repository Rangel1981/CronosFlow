from pydantic import BaseModel, EmailStr

from src.models.user import RegimeTrabalho

class UserBase(BaseModel): 
    nome: str
    email: EmailStr
    regime: RegimeTrabalho
    carga_horaria_diaria: int = 480 
    valor_hora: float = 0.0


class UserCreate(UserBase):#User In - entrada
    password: str

class UserResponse(UserBase): #User out - saida
    id: int
    is_active: bool


    # configurando o objeto do banco para o schema
    class Config:
        from_attributes = True