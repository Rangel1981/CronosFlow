from datetime import datetime, date, timedelta
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.ponto import JornadaDiaria, RegistroPonto, PontosBatidos
from src.schemas.ponto import RegistroPontoCreate, RegistroPontoUpdate

class PontoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_jornada_hoje(self, usuario_id: int) -> JornadaDiaria | None:
        hoje = date.today()
        query = select(JornadaDiaria).where(
            JornadaDiaria.id_user == usuario_id,
            JornadaDiaria.data == hoje
        )
        return self.db.execute(query).scalar_one_or_none()

    def get_proximo_tipo_ponto(self, jornada: JornadaDiaria) -> PontosBatidos:
        qtd_pontos = len(jornada.pontos)

        if qtd_pontos == 0:
            return PontosBatidos.ENTRADA
        elif qtd_pontos == 1:
            return PontosBatidos.ALMOCO_SAIDA
        elif qtd_pontos == 2:
            return PontosBatidos.ALMOCO_ENTRADA  
        else:
            return PontosBatidos.SAIDA

    def listar_pontos_por_usuario(self, usuario_id: int) -> List[JornadaDiaria]:
        query = (
            select(JornadaDiaria)
            .where(JornadaDiaria.id_user == usuario_id)
            .order_by(JornadaDiaria.data.desc()) 
        )
        return self.db.execute(query).scalars().all()

    def bater_ponto(self, ponto_in: RegistroPontoCreate) -> RegistroPonto:
        jornada = self.get_jornada_hoje(ponto_in.usuario_id)

        if jornada and not jornada.status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A jornada de hoje já foi encerrada e não aceita novos pontos."
            )

        if jornada and jornada.pontos:
            ultimo_ponto = max(jornada.pontos, key=lambda p: p.horario)
            tempo_decorrido = datetime.now() - ultimo_ponto.horario
            
            if tempo_decorrido < timedelta(minutes=1):
                tempo_restante = int(60 - tempo_decorrido.total_seconds())
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ponto já registrado recentemente. Aguarde {tempo_restante} segundos para bater novamente."
                )

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

        novo_ponto = RegistroPonto(
            id_jornada=jornada.id,      
            horario=datetime.now(),
            registro=tipo_detectado     
        )
        self.db.add(novo_ponto)
        self.db.flush() 

        if tipo_detectado == PontosBatidos.SAIDA:
            batidas = sorted(jornada.pontos, key=lambda p: p.horario)
            
            if len(batidas) >= 4:
                t1 = batidas[0].horario
                t2 = batidas[1].horario
                t3 = batidas[2].horario
                t4 = batidas[3].horario

                periodo_1 = t2 - t1
                periodo_2 = t4 - t3
                
                total_trabalhado = periodo_1 + periodo_2
                minutos_trabalhados = int(total_trabalhado.total_seconds() / 60)

                jornada.saldo_horas = minutos_trabalhados
                jornada.status = False
                self.db.add(jornada)

        self.db.commit()
        self.db.refresh(novo_ponto)
        return novo_ponto

    def atualizar_ponto(self, ponto_id: int, ponto_in: RegistroPontoUpdate) -> RegistroPonto:
        query_ponto = select(RegistroPonto).where(RegistroPonto.id == ponto_id)
        ponto = self.db.execute(query_ponto).scalar_one_or_none()

        if not ponto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de ponto não encontrado."
            )

        ponto.horario = ponto_in.horario.replace(tzinfo=None)
        self.db.flush()

        jornada = ponto.jornada
        if jornada:
            batidas = sorted(jornada.pontos, key=lambda p: p.horario)
            
            if len(batidas) >= 4:
                t1 = batidas[0].horario
                t2 = batidas[1].horario
                t3 = batidas[2].horario
                t4 = batidas[3].horario

                periodo_1 = t2 - t1
                periodo_2 = t4 - t3
                
                total_trabalhado = periodo_1 + periodo_2
                minutos_trabalhados = int(total_trabalhado.total_seconds() / 60)

                jornada.saldo_horas = minutos_trabalhados
                self.db.add(jornada)

        self.db.commit()
        self.db.refresh(ponto)
        return ponto