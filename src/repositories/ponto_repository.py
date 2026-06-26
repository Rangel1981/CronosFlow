from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.ponto import JornadaDiaria, RegistroPonto, PontosBatidos
from src.schemas.ponto import RegistroPontoCreate, List, RegistroPontoCreate

class PontoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_jornada_hoje(self, usuario_id: int) -> JornadaDiaria | None:
        """
        Busca se o usuário já tem uma jornada aberta na data de hoje.
        """
        hoje = date.today()
        query = select(JornadaDiaria).where(
            JornadaDiaria.id_user == usuario_id,
            JornadaDiaria.data == hoje
        )
        return self.db.execute(query).scalar_one_or_none()

    def get_proximo_tipo_ponto(self, jornada: JornadaDiaria) -> PontosBatidos:
        """
        Conta quantos pontos o usuário já bateu hoje para deduzir o próximo tipo
        baseado no Enum real do seu modelo (PontosBatidos).
        """
        qtd_pontos = len(jornada.pontos)

        if qtd_pontos == 0:
            return PontosBatidos.ENTRADA
        elif qtd_pontos == 1:
            return PontosBatidos.ALMOCO_SAIDA
        elif qtd_pontos == 2:
            return PontosBatidos.ALMOCO_ENTRADA  
        else:
            return PontosBatidos.SAIDA

    def bater_ponto(self, ponto_in: RegistroPontoCreate) -> RegistroPonto:
        """
        Método principal: Verifica a jornada, decide o tipo de ponto,
        salva no banco e retorna o registro carimbado.
        """
        jornada = self.get_jornada_hoje(ponto_in.usuario_id)

        # Se não existir jornada para hoje, cria uma nova
        if not jornada:
            jornada = JornadaDiaria(
                id_user=ponto_in.usuario_id,
                data=date.today(),
                status=True,       
                saldo_horas=0     
            )
            self.db.add(jornada)
            self.db.commit()
            self.db.refresh(jornada)

        tipo_detectado = self.get_proximo_tipo_ponto(jornada)

        # Cria o registro de ponto respeitando os nomes do seu modelo
        novo_ponto = RegistroPonto(
            id_jornada=jornada.id,      
            horario=datetime.now(),
            registro=tipo_detectado,    
            
        )

        self.db.add(novo_ponto)
        self.db.commit()
        self.db.refresh(novo_ponto)

        return novo_ponto
    
    def listar_pontos_por_usuario(self, usuario_id: int) -> List[JornadaDiaria]:
            """
            Busca todo o histórico de jornadas e pontos de um usuário específico.
            """
            query = (
                select(JornadaDiaria)
                .where(JornadaDiaria.id_user == usuario_id)
                .order_by(JornadaDiaria.data.desc()) # Traz os dias mais recentes primeiro
            )
            return self.db.execute(query).scalars().all()