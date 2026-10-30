
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from infrastructure.database import Base

if TYPE_CHECKING:
    from infrastructure.models.empresa_model import EmpresaModel
    from infrastructure.models.espacio_model import EspacioModel


class ReservaModel(Base):
    __tablename__ = "reservas"

    __table_args__ = (
        CheckConstraint(
            "fecha_fin > fecha_inicio",
            name="ck_reservas_fechas_validas",
        ),
        CheckConstraint(
            "estado IN ('pendiente', 'confirmada', 'cancelada')",
            name="ck_reservas_estado_valido",
        ),
        Index(
            "ix_reservas_espacio_fechas",
            "espacio_id",
            "fecha_inicio",
            "fecha_fin",
        ),
        Index(
            "ix_reservas_empresa_fechas",
            "empresa_id",
            "fecha_inicio",
            "fecha_fin",
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

    empresa_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("empresas.id"),
        nullable=False,
    )

    fecha_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    fecha_fin: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="confirmada",
    )

    # Relaciones
    espacio: Mapped["EspacioModel"] = relationship(
        back_populates="reservas",
    )

    empresa: Mapped["EmpresaModel"] = relationship(
        back_populates="reservas",
    )
