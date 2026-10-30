from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from domain.empresa_domain import Empresa
from infrastructure.mappers import empresa_mapper
from infrastructure.models.empresa_model import EmpresaModel


class EmpresaRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, empresa: Empresa) -> Empresa:
        modelo = empresa_mapper.a_model(empresa)

        try:
            self.session.add(modelo)
            self.session.flush()
            self.session.refresh(modelo)
            return empresa_mapper.a_domain(modelo)
        except Exception:
            self.session.rollback()
            raise

    def obtener_por_id(self, empresa_id: UUID) -> Empresa | None:
        modelo = self.session.get(EmpresaModel, empresa_id)

        if modelo is None:
            return None

        return empresa_mapper.a_domain(modelo)

    def obtener_por_rut(self, rut: str) -> Empresa | None:
        rut_buscado = rut.strip().upper().replace(".", "")

        modelo = self.session.scalars(
            select(EmpresaModel).where(
                func.upper(
                    func.replace(EmpresaModel.rut, ".", "")
                ) == rut_buscado
            )
        ).first()

        if modelo is None:
            return None

        return empresa_mapper.a_domain(modelo)

    def listar(
        self,
        offset: int = 0,
        limite: int = 10,
        activa: bool | None = None,
    ) -> list[Empresa]:
        consulta = select(EmpresaModel)

        if activa is not None:
            consulta = consulta.where(EmpresaModel.activa == activa)

        modelos = self.session.scalars(
            consulta
            .order_by(EmpresaModel.nombre, EmpresaModel.id)
            .offset(offset)
            .limit(limite)
        ).all()

        return [
            empresa_mapper.a_domain(modelo)
            for modelo in modelos
        ]

    def contar(self, activa: bool | None = None) -> int:
        consulta = select(func.count()).select_from(EmpresaModel)

        if activa is not None:
            consulta = consulta.where(EmpresaModel.activa == activa)

        return self.session.scalar(consulta) or 0

    def actualizar(self, empresa: Empresa) -> Empresa:
        modelo = self.session.get(EmpresaModel, empresa.id)

        if modelo is None:
            raise ValueError("La empresa no existe.")

        try:
            empresa_mapper.actualizar_model(modelo, empresa)
            self.session.flush()
            self.session.refresh(modelo)
            return empresa_mapper.a_domain(modelo)
        except Exception:
            self.session.rollback()
            raise

    def eliminar(self, empresa_id: UUID) -> bool:
        modelo = self.session.get(EmpresaModel, empresa_id)

        if modelo is None:
            return False

        try:
            self.session.delete(modelo)
            self.session.flush()
            return True
        except Exception:
            self.session.rollback()
            raise
