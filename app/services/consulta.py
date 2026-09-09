from sqlalchemy.orm import Session

from app.models.consulta import Consulta, ConsultaStatus
from app.schemas.consulta import ConsultaCreate, ConsultaListResponse, ConsultaResponse
from app.core.logging import logger
from app.core.exceptions import AppException
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status
import time


def get_all_consultas(
    db: Session,
    *,
    status_filtro: ConsultaStatus | None = None,
    documento: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> ConsultaListResponse:
    tempo_inicial = time.perf_counter()

    logger.info(
        "Buscando registros de consulta - status=%s - documento=%s - page=%s - page_size=%s",
        status_filtro,
        documento,
        page,
        page_size,
    )

    try:
        query = db.query(Consulta)

        if status_filtro is not None:
            query = query.filter(Consulta.status == status_filtro)

        if documento is not None:
            query = query.filter(Consulta.documento == documento)

        total = query.count()
        consultas = (
            query.order_by(Consulta.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        tempo_final = time.perf_counter() - tempo_inicial

        logger.info(
            "Registros encontrados com sucesso - quantidade=%s - total=%s - tempo_execucao=%s",
            len(consultas),
            total,
            tempo_final,
        )

        pages = (total + page_size - 1) // page_size if page_size else 0

        return ConsultaListResponse(
            items=consultas,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    except SQLAlchemyError:
        db.rollback()
        raise AppException(
            code="DATABASE_ERROR",
            message="Erro ao buscar todos os registros de consulta",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

def get_consulta_by_id(db: Session, consulta_id: int) -> Consulta:
    tempo_inicial = time.perf_counter()
    try:
        logger.info(
            "Buscando registro de consulta - consulta_id=%s",
            consulta_id,
        )

        consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()

        if consulta is None:
            raise AppException(
                code="NOT_FOUND",
                message="Registro de consulta não encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        tempo_final = time.perf_counter() - tempo_inicial

        logger.info(
            "Registro encontrado com sucesso - consulta_id=%s - tempo_execucao=%s",
            consulta_id,
            tempo_final,
        )

        return ConsultaResponse.model_validate(consulta).model_dump(exclude_none=True)

    except SQLAlchemyError as error:
        logger.error(
            "Erro ao buscar registro de consulta - consulta_id=%s - error=%s",
            consulta_id,
            error,
        )
        db.rollback()
        raise AppException(
            code="DATABASE_ERROR",
            message="Erro ao buscar registro de consulta",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

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