from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.schemas.consulta import ConsultaCreate, ConsultaResponse
from app.services.consulta import create_consulta

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