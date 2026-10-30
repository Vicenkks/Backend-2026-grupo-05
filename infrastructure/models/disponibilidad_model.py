
from datetime import time
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    Time,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database import Base

if TYPE_CHECKING:
    from infrastructure.models.espacio_model import EspacioModel

class DisponibilidadModel(Base):
    __tablename__ = "disponibilidades"

    __table_args__ = (
        CheckConstraint(
            "dia_semana BETWEEN 0 AND 6",
            name="ck_disponibilidades_dia_valido",
        ),
        CheckConstraint(
            "hora_cierre > hora_apertura",
            name="ck_disponibilidades_horario_valido",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    espacio_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("espacios.id"),
        nullable=False,
    )

    dia_semana: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    hora_apertura: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    hora_cierre: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    activa: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    # Relaciones
    espacio: Mapped["EspacioModel"] = relationship(
        back_populates="disponibilidades",
    )
