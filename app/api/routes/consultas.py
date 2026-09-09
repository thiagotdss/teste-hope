from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.consulta import ConsultaStatus
from app.schemas.consulta import ConsultaCreate, ConsultaListResponse, ConsultaResponse
from app.services.consulta import create_consulta, get_all_consultas, get_consulta_by_id
import uuid

router = APIRouter(
    prefix="/api/v1/consultas",
    tags=["Consultas"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get(
    "",
    response_model=ConsultaListResponse,
    status_code=status.HTTP_200_OK,
)
def get_all(
    db: Session = Depends(get_db),
    status_filtro: ConsultaStatus | None = Query(default=None, alias="status"),
    documento: str | None = Query(default=None, min_length=11, max_length=14),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    return get_all_consultas(
        db,
        status_filtro=status_filtro,
        documento=documento,
        page=page,
        page_size=page_size,
    )

@router.get(
    "/{consulta_id}",
    response_model=ConsultaResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
def get_by_id(
    consulta_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return get_consulta_by_id(db, consulta_id=consulta_id)

@router.post(
    "",
    response_model=ConsultaResponse,
    status_code=status.HTTP_201_CREATED,
)
def create(
    dados: ConsultaCreate,
    db: Session = Depends(get_db),
):
    return create_consulta(db, dados)