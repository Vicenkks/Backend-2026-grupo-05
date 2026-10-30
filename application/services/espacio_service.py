from uuid import UUID, uuid4
from domain.espacio_domain import (
    Espacio,
    TipoEspacio,
    EstadoEspacio,
)
from infrastructure.repositories.espacio_repository import (
    EspacioRepository,
)


class EspacioService:
    def __init__(
        self,
        repository: EspacioRepository,
    ) -> None:
        self.repository = repository

    def crear(
        self,
        nombre: str,
        tipo: TipoEspacio,
        capacidad: int,
        estado: EstadoEspacio = EstadoEspacio.ACTIVO,
    ) -> Espacio:
        espacio = Espacio(
            id=uuid4(),
            nombre=nombre,
            tipo=tipo,
            capacidad=capacidad,
            estado=estado,
        )

        self._validar_espacio(espacio)

        return self.repository.crear(espacio)

    def obtener(self, espacio_id: UUID) -> Espacio | None:
        return self.repository.obtener_por_id(espacio_id)

    def listar(
        self,
        pagina: int,
        tamano: int,
        tipo: str | None = None,
        estado: str | None = None,
        ordenar_por: str = "nombre",
        direccion: str = "asc",
    ) -> tuple[list[Espacio], int]:
        if pagina < 1:
            raise ValueError(
                "La página debe ser mayor o igual a 1."
            )

        if tamano < 1 or tamano > 100:
            raise ValueError(
                "El tamaño debe estar entre 1 y 100."
            )

        offset = (pagina - 1) * tamano

        espacios = self.repository.listar(
            offset=offset,
            limite=tamano,
            tipo=tipo,
            estado=estado,
            ordenar_por=ordenar_por,
            direccion=direccion,
        )

        total = self.repository.contar(
            tipo=tipo,
            estado=estado,
        )

        return espacios, total

    def actualizar(
        self,
        espacio_id: UUID,
        nombre: str,
        tipo: TipoEspacio,
        capacidad: int,
        estado: EstadoEspacio,
    ) -> Espacio | None:
        actual = self.repository.obtener_por_id(espacio_id)

        if actual is None:
            return None

        actualizado = Espacio(
            id=actual.id,
            nombre=nombre,
            tipo=tipo,
            capacidad=capacidad,
            estado=estado,
        )

        self._validar_espacio(actualizado)

        return self.repository.actualizar(actualizado)

    def eliminar(self, espacio_id: UUID) -> bool:
        return self.repository.eliminar(espacio_id)

    def _validar_espacio(self, espacio: Espacio) -> None:
        if not espacio.nombre.strip():
            raise ValueError(
                "El nombre del espacio es obligatorio."
            )

        if espacio.capacidad < 1:
            raise ValueError(
                "La capacidad debe ser mayor que cero."
            )
