from domain.errors import Conflict

from uuid import UUID, uuid4

from domain.empresa_domain import Empresa
from infrastructure.repositories.empresa_repository import (
    EmpresaRepository,
)


class EmpresaService:
    def __init__(
        self,
        repository: EmpresaRepository,
    ) -> None:
        self.repository = repository

    def crear(
        self,
        nombre: str,
        rut: str,
        contacto: str,
        activa: bool = True,
    ) -> Empresa:
        empresa = Empresa(
            id=uuid4(),
            nombre=nombre.strip(),
            rut=rut.strip().upper().replace(".", "").replace("-", ""),
            contacto=contacto.strip(),
            activa=activa,
        )

        self._validar_empresa(empresa)
        self._validar_rut_disponible(empresa.rut)

        return self.repository.crear(empresa)

    def obtener(self, empresa_id: UUID) -> Empresa | None:
        return self.repository.obtener_por_id(empresa_id)

    def listar(
        self,
        pagina: int,
        tamano: int,
        activa: bool | None = None,
    ) -> tuple[list[Empresa], int]:
        if pagina < 1:
            raise ValueError(
                "La página debe ser mayor o igual a 1."
            )

        if tamano < 1 or tamano > 100:
            raise ValueError(
                "El tamaño debe estar entre 1 y 100."
            )

        offset = (pagina - 1) * tamano

        empresas = self.repository.listar(
            offset=offset,
            limite=tamano,
            activa=activa,
        )

        total = self.repository.contar(activa=activa)

        return empresas, total

    def actualizar(
        self,
        empresa_id: UUID,
        nombre: str,
        rut: str,
        contacto: str,
        activa: bool,
    ) -> Empresa | None:
        actual = self.repository.obtener_por_id(empresa_id)

        if actual is None:
            return None

        actualizada = Empresa(
            id=actual.id,
            nombre=nombre.strip(),
            rut=rut.strip().upper().replace(".", "").replace("-", ""),
            contacto=contacto.strip(),
            activa=activa,
        )

        self._validar_empresa(actualizada)
        self._validar_rut_disponible(
            rut=actualizada.rut,
            empresa_id=empresa_id,
        )

        return self.repository.actualizar(actualizada)

    def eliminar(self, empresa_id: UUID) -> bool:
        return self.repository.eliminar(empresa_id)

    def _validar_empresa(self, empresa: Empresa) -> None:
        if not empresa.nombre:
            raise ValueError(
                "El nombre de la empresa es obligatorio."
            )

        if not empresa.rut:
            raise ValueError("El RUT es obligatorio.")

        if not empresa.contacto:
            raise ValueError(
                "El contacto de la empresa es obligatorio."
            )

    def _validar_rut_disponible(
        self,
        rut: str,
        empresa_id: UUID | None = None,
    ) -> None:
        existente = self.repository.obtener_por_rut(rut)

        if existente is not None and existente.id != empresa_id:
            raise Conflict(
                "Ya existe una empresa con ese RUT."
            )
