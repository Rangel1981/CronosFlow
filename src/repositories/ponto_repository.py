
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.core.ponto import JornadaDiaria, RegistroPonto
from src.schemas.ponto import RegistroPontoCreate

class PontoRepository:
    def __init__(self, db: Session):
        """
        O construtor recebe a sessão do banco para executar os comandos.
        """
        self.db = db

    def get_jornada_hoje(self, usuario_id: int) -> JornadaDiaria | None:
        """
        Busca se o usuário já tem uma jornada aberta na data de hoje.
        """
        hoje = date.today()
        query = select(JornadaDiaria).where(
            JornadaDiaria.usuario_id == usuario_id,
            JornadaDiaria.data == hoje
        )
        return self.db.execute(query).scalar_one_or_none()

    def get_proximo_tipo_ponto(self, jornada: JornadaDiaria) -> str:
        """
        Conta quantos pontos o usuário já bateu hoje para deduzir o próximo tipo.
        Se você criou um Enum no banco, pode retornar o Enum em vez de string pura.
        """
        qtd_pontos = len(jornada.pontos)

        if qtd_pontos == 0:
            return "ENTRADA"
        elif qtd_pontos == 1:
            return "ALMOCO_SAIDA"
        elif qtd_pontos == 2:
            return "ALMOCO_RETORNO"
        else:
            return "SAIDA"

    def bater_ponto(self, ponto_in: RegistroPontoCreate) -> RegistroPonto:
        """
        Método principal: Verifica a jornada, decide o tipo de ponto,
        salva no banco e retorna o registro carimbado.
        """
        # 1. Verifica se já existe jornada para hoje
        jornada = self.get_jornada_hoje(ponto_in.usuario_id)

        # 2. Se não existir, cria a jornada do dia
        if not jornada:
            jornada = JornadaDiaria(
                usuario_id=ponto_in.usuario_id,
                data=date.today(),
                fechada=False,
                horas_trabalhadas=0.0
            )
            self.db.add(jornada)
            self.db.commit()
            self.db.refresh(jornada)

        # 3. Descobre qual o próximo tipo de ponto (Entrada, Almoço, Saída...)
        tipo_detectado = self.get_proximo_tipo_ponto(jornada)

        # 4. Cria o registro de ponto com o horário exato do servidor
        novo_ponto = RegistroPonto(
            jornada_id=jornada.id,
            horario=datetime.now(),
            tipo_ponto=tipo_detectado,
            observacao=ponto_in.observacao
        )

        self.db.add(novo_ponto)
        self.db.commit()
        self.db.refresh(novo_ponto)

        return novo_ponto