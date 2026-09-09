from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.consulta import ConsultaStatus


class ConsultaCreate(BaseModel):
    documento: str = Field(min_length=11, max_length=14)
    tipo: str = Field(min_length=1, max_length=10)

    @field_validator("documento")
    @classmethod
    def validar_documento(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Documento informado é inválido.")

        if len(value) not in (11, 14):
            raise ValueError("Documento informado é inválido.")

        return value


class ConsultaResponse(BaseModel):
    id: UUID
    documento: str
    tipo: str
    status: ConsultaStatus
    tentativas: int
    resultado: dict | None
    ultimo_erro: str | None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None

    model_config = {
        "from_attributes": True
    }