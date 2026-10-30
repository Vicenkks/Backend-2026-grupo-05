from uuid import UUID, uuid4
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base

if TYPE_CHECKING:
    from infrastructure.models.reserva_model import ReservaModel

class EmpresaModel(Base):
    __tablename__ = "empresas"

    __table_args__ = (
        CheckConstraint(
            "length(trim(nombre)) > 0",
            name="ck_empresas_nombre_no_vacio",
        ),
        CheckConstraint(
            "length(trim(rut)) > 0",
            name="ck_empresas_rut_no_vacio",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    nombre: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    rut: Mapped[str] = mapped_column(
        String(12),
        nullable=False,
        unique=True,
        index=True,
    )

    contacto: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    activa: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
    )

    # Relaciones
    reservas: Mapped[list["ReservaModel"]] = relationship(
        back_populates="empresa",
    )
