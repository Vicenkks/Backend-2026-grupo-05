from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.disponibilidad_domain import Disponibilidad
from infrastructure.mappers import disponibilidad_mapper
from infrastructure.models.disponibilidad_model import DisponibilidadModel


class DisponibilidadRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(
        self,
        disponibilidad: Disponibilidad,
    ) -> Disponibilidad:
        modelo = disponibilidad_mapper.a_model(disponibilidad)

        try:
            self.session.add(modelo)
            self.session.flush()
            self.session.refresh(modelo)
            return disponibilidad_mapper.a_domain(modelo)
        except Exception:
            self.session.rollback()
            raise

    def obtener_por_id(
        self,
        disponibilidad_id: UUID,
    ) -> Disponibilidad | None:
        modelo = self.session.get(
            DisponibilidadModel,
            disponibilidad_id,
        )

        if modelo is None:
            return None

        return disponibilidad_mapper.a_domain(modelo)

    def listar(
        self,
        offset: int = 0,
        limite: int = 10,
        espacio_id: UUID | None = None,
        dia_semana: int | None = None,
        activa: bool | None = None,
    ) -> list[Disponibilidad]:
        consulta = select(DisponibilidadModel)

        if espacio_id is not None:
            consulta = consulta.where(
                DisponibilidadModel.espacio_id == espacio_id
            )

        if dia_semana is not None:
            consulta = consulta.where(
                DisponibilidadModel.dia_semana == dia_semana
            )

        if activa is not None:
            consulta = consulta.where(
                DisponibilidadModel.activa == activa
            )

        modelos = self.session.scalars(
            consulta
            .order_by(
                DisponibilidadModel.dia_semana,
                DisponibilidadModel.hora_apertura,
                DisponibilidadModel.id,
            )
            .offset(offset)
            .limit(limite)
        ).all()

        return [
            disponibilidad_mapper.a_domain(modelo)
            for modelo in modelos
        ]

    def contar(
        self,
        espacio_id: UUID | None = None,
        dia_semana: int | None = None,
        activa: bool | None = None,
    ) -> int:
        consulta = select(func.count()).select_from(
            DisponibilidadModel
        )

        if espacio_id is not None:
            consulta = consulta.where(
                DisponibilidadModel.espacio_id == espacio_id
            )

        if dia_semana is not None:
            consulta = consulta.where(
                DisponibilidadModel.dia_semana == dia_semana
            )

        if activa is not None:
            consulta = consulta.where(
                DisponibilidadModel.activa == activa
            )

        return self.session.scalar(consulta) or 0

    def actualizar(
        self,
        disponibilidad: Disponibilidad,
    ) -> Disponibilidad:
        modelo = self.session.get(
            DisponibilidadModel,
            disponibilidad.id,
        )

        if modelo is None:
            raise ValueError("La disponibilidad no existe.")

        try:
            disponibilidad_mapper.actualizar_model(
                modelo,
                disponibilidad,
            )
            self.session.flush()
            self.session.refresh(modelo)
            return disponibilidad_mapper.a_domain(modelo)
        except Exception:
            self.session.rollback()
            raise

    def eliminar(self, disponibilidad_id: UUID) -> bool:
        modelo = self.session.get(
            DisponibilidadModel,
            disponibilidad_id,
        )

        if modelo is None:
            return False

        try:
            self.session.delete(modelo)
            self.session.flush()
            return True
        except Exception:
            self.session.rollback()
            raise
