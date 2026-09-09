from sqlalchemy.orm import Session

from app.models.consulta import Consulta
from app.schemas.consulta import ConsultaCreate
from app.core.logging import logger
from app.core.exceptions import AppException
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status

import time



def create_consulta(db: Session, dados: ConsultaCreate) -> Consulta:
    tempo_inicial = time.perf_counter()

    logger.info(
        "Criando registro para consulta - documento=%s",
        dados.documento,
    )

    try:
        consulta = Consulta(
            documento=dados.documento,
            tipo=dados.tipo,
        )

        db.add(consulta)
        db.commit()
        db.refresh(consulta)

        tempo_final = time.perf_counter() - tempo_inicial

        logger.info(
            "Registro criado com sucesso - consulta_id=%s - tempo_execucao=%s",
            consulta.id,
            tempo_final,
        )

        return consulta

    except SQLAlchemyError:
        db.rollback()

        tempo_final = time.perf_counter() - tempo_inicial

        logger.exception(
            "Erro ao criar registro para consulta - documento=%s - tempo_execucao=%s",
            dados.documento,
            tempo_final,
        )

        raise AppException(
            code="DATABASE_ERROR",
            message="Erro ao criar registro para consulta",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )