
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.espacio_domain import Espacio
from infrastructure.mappers import espacio_mapper
from infrastructure.models.espacio_model import EspacioModel


class EspacioRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, espacio: Espacio) -> Espacio:
        modelo = espacio_mapper.a_modelo(espacio)

        try:
            self.session.add(modelo)
            self.session.flush()
            self.session.refresh(modelo)
            return espacio_mapper.a_dominio(modelo)
        except Exception:
            self.session.rollback()
            raise

    def obtener_por_id(self, espacio_id: UUID) -> Espacio | None:
        modelo = self.session.get(EspacioModel, espacio_id)

        if modelo is None:
            return None

        return espacio_mapper.a_dominio(modelo)

    def listar(
        self,
        offset: int = 0,
        limite: int = 10,
        tipo: str | None = None,
        estado: str | None = None,
        ordenar_por: str = "nombre",
        direccion: str = "asc",
    ) -> list[Espacio]:
        consulta = select(EspacioModel)

        if tipo is not None:
            consulta = consulta.where(EspacioModel.tipo == tipo)

        if estado is not None:
            consulta = consulta.where(EspacioModel.estado == estado)

        columnas = {key: getattr(EspacioModel, key) for key in ("nombre", "capacidad", "tipo", "estado")}
        columna = columnas[ordenar_por]
        orden = columna.desc() if direccion == "desc" else columna.asc()
        modelos = self.session.scalars(
            consulta
            .order_by(orden, EspacioModel.id)
            .offset(offset)
            .limit(limite)
        ).all()

        return [
            espacio_mapper.a_dominio(modelo)
            for modelo in modelos
        ]

    def contar(
        self,
        tipo: str | None = None,
        estado: str | None = None,
    ) -> int:
        consulta = select(func.count()).select_from(EspacioModel)

        if tipo is not None:
            consulta = consulta.where(EspacioModel.tipo == tipo)

        if estado is not None:
            consulta = consulta.where(EspacioModel.estado == estado)

        return self.session.scalar(consulta) or 0

    def actualizar(self, espacio: Espacio) -> Espacio:
        modelo = self.session.get(EspacioModel, espacio.id)

        if modelo is None:
            raise ValueError("El espacio no existe.")

        try:
            espacio_mapper.actualizar_modelo(modelo, espacio)
            self.session.flush()
            self.session.refresh(modelo)
            return espacio_mapper.a_dominio(modelo)
        except Exception:
            self.session.rollback()
            raise

    def eliminar(self, espacio_id: UUID) -> bool:
        modelo = self.session.get(EspacioModel, espacio_id)

        if modelo is None:
            return False

        try:
            self.session.delete(modelo)
            self.session.flush()
            return True
        except Exception:
            self.session.rollback()
            raise
