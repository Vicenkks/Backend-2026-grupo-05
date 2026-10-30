from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.reserva_domain import Reserva, EstadoReserva
from infrastructure.mappers import reserva_mapper
from infrastructure.models.reserva_model import ReservaModel


class ReservaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, reserva: Reserva) -> Reserva:
        modelo = reserva_mapper.a_model(reserva)

        try:
            self.session.add(modelo)
            self.session.flush()
            self.session.refresh(modelo)
            return reserva_mapper.a_domain(modelo)
        except Exception:
            self.session.rollback()
            raise

    def obtener_por_id(self, reserva_id: UUID) -> Reserva | None:
        modelo = self.session.get(ReservaModel, reserva_id)

        if modelo is None:
            return None

        return reserva_mapper.a_domain(modelo)

    def listar(
        self,
        offset: int = 0,
        limite: int = 10,
        espacio_id: UUID | None = None,
        empresa_id: UUID | None = None,
        estado: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> list[Reserva]:
        consulta = select(ReservaModel)

        if espacio_id is not None:
            consulta = consulta.where(
                ReservaModel.espacio_id == espacio_id
            )

        if empresa_id is not None:
            consulta = consulta.where(
                ReservaModel.empresa_id == empresa_id
            )

        if estado is not None:
            consulta = consulta.where(
                ReservaModel.estado == estado
            )

        if desde is not None:
            consulta = consulta.where(
                ReservaModel.fecha_inicio >= desde
            )

        if hasta is not None:
            consulta = consulta.where(
                ReservaModel.fecha_inicio <= hasta
            )

        modelos = self.session.scalars(
            consulta
            .order_by(ReservaModel.fecha_inicio, ReservaModel.id)
            .offset(offset)
            .limit(limite)
        ).all()

        return [
            reserva_mapper.a_domain(modelo)
            for modelo in modelos
        ]

    def contar(
        self,
        espacio_id: UUID | None = None,
        empresa_id: UUID | None = None,
        estado: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> int:
        consulta = select(func.count()).select_from(ReservaModel)

        if espacio_id is not None:
            consulta = consulta.where(
                ReservaModel.espacio_id == espacio_id
            )

        if empresa_id is not None:
            consulta = consulta.where(
                ReservaModel.empresa_id == empresa_id
            )

        if estado is not None:
            consulta = consulta.where(
                ReservaModel.estado == estado
            )

        if desde is not None:
            consulta = consulta.where(ReservaModel.fecha_inicio >= desde)
        if hasta is not None:
            consulta = consulta.where(ReservaModel.fecha_inicio <= hasta)
        return self.session.scalar(consulta) or 0

    def existe_solapamiento_espacio(
        self,
        espacio_id: UUID,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        excluir_reserva_id: UUID | None = None,
    ) -> bool:
        estados_activos = [
            EstadoReserva.PENDIENTE.value,
            EstadoReserva.CONFIRMADA.value,
        ]

        consulta = select(ReservaModel.id).where(
            ReservaModel.espacio_id == espacio_id,
            ReservaModel.estado.in_(estados_activos),
            ReservaModel.fecha_inicio < fecha_fin,
            ReservaModel.fecha_fin > fecha_inicio,
        )

        if excluir_reserva_id is not None:
            consulta = consulta.where(
                ReservaModel.id != excluir_reserva_id
            )

        return self.session.scalars(consulta).first() is not None

    def existe_solapamiento_empresa(
        self,
        empresa_id: UUID,
        fecha_inicio: datetime,
        fecha_fin: datetime,
        excluir_reserva_id: UUID | None = None,
    ) -> bool:
        estados_activos = [
            EstadoReserva.PENDIENTE.value,
            EstadoReserva.CONFIRMADA.value,
        ]

        consulta = select(ReservaModel.id).where(
            ReservaModel.empresa_id == empresa_id,
            ReservaModel.estado.in_(estados_activos),
            ReservaModel.fecha_inicio < fecha_fin,
            ReservaModel.fecha_fin > fecha_inicio,
        )

        if excluir_reserva_id is not None:
            consulta = consulta.where(
                ReservaModel.id != excluir_reserva_id
            )

        return self.session.scalars(consulta).first() is not None

    def actualizar(self, reserva: Reserva) -> Reserva:
        modelo = self.session.get(ReservaModel, reserva.id)

        if modelo is None:
            raise ValueError("La reserva no existe.")

        try:
            reserva_mapper.actualizar_modelo(modelo, reserva)
            self.session.flush()
            self.session.refresh(modelo)
            return reserva_mapper.a_domain(modelo)
        except Exception:
            self.session.rollback()
            raise

    def eliminar(self, reserva_id: UUID) -> bool:
        modelo = self.session.get(ReservaModel, reserva_id)

        if modelo is None:
            return False

        try:
            self.session.delete(modelo)
            self.session.flush()
            return True
        except Exception:
            self.session.rollback()
            raise
