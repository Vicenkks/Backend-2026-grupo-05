from uuid import UUID, uuid4
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base

if TYPE_CHECKING:
    from infrastructure.models.disponibilidad_model import DisponibilidadModel
    from infrastructure.models.reserva_model import ReservaModel



class EspacioModel(Base):
    __tablename__ = "espacios"

    __table_args__ = (
        CheckConstraint(
            "capacidad > 0",
            name="ck_espacios_capacidad_positiva",
        ),
        CheckConstraint(
            "tipo IN ('sala_reunion', 'escritorio', 'oficina')",
            name="ck_espacios_tipo_valido",
        ),
        CheckConstraint(
            "estado IN ('activo', 'inactivo', 'mantenimiento')",
            name="ck_espacios_estado_valido",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    tipo: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    capacidad: Mapped[int] = mapped_column(
        nullable=False,
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="activo",
    )

    # Relaciones
    reservas: Mapped[list["ReservaModel"]] = relationship(
        back_populates="espacio",
    )

    disponibilidades: Mapped[list["DisponibilidadModel"]] = relationship(
        back_populates="espacio",
    )
