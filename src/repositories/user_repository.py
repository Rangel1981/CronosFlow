from sqlalchemy.orm import Session
from sqlalchemy import select
from src.models.user import User
from src.schemas.user import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email:str) -> User | None:
        """
        Busca um usuário no banco pelo e-mail.
        Se não encontrar, retorna None.
        """
        #criando uma query de seleção baseada na tabela User
        query = select(User).where(User.email == email)

        #usando o .scalar_one_or_none() na query, vai retornar o objeto ou none se não achar
        result = self.db.execute(query).scalar_one_or_none()
        return result
    
    def create(self, user_schema: UserCreate, hashed_password: str) -> User:
        """
        Recebe os dados validados do Pydantic (user_schema) + a senha criptografada,
        converte para o modelo do SQLAlchemy e salva no banco de dados.
        """
        # transformando o Schema do Pydantic em um dicionário Python (ignorando o password original)
        user_data = user_schema.model_dump(exclude={"password"})

        #instanciando o modelo do SQLAlchemy passando os dados + a senha já criptografada
        db_user = User(**user_data, hashed_password=hashed_password)

        #colocando o objeto na fila do banco de dados
        self.db.add(db_user)

        #confirmando a transição para salvar fisicamente no arquivo .db
        self.db.commit()

        #atualizando o objeto para que venha com o id
        self.db.refresh(db_user)

        return db_user