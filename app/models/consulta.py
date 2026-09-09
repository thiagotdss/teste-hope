import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ConsultaStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class Consulta(Base):
    __tablename__ = "consultas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    documento: Mapped[str] = mapped_column(
        String(14),
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    status: Mapped[ConsultaStatus] = mapped_column(
        SQLEnum(ConsultaStatus),
        nullable=False,
        default=ConsultaStatus.PENDING,
    )

    tentativas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    resultado: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    ultimo_erro: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
