from domain.errors import ResourceNotFound, Conflict

from datetime import time
from uuid import UUID, uuid4

from domain.disponibilidad_domain import Disponibilidad
from infrastructure.repositories.disponibilidad_repository import (
    DisponibilidadRepository,
)
from infrastructure.repositories.espacio_repository import (
    EspacioRepository,
)


class DisponibilidadService:
    def __init__(
        self,
        repository: DisponibilidadRepository,
        espacio_repository: EspacioRepository,
    ) -> None:
        self.repository = repository
        self.espacio_repository = espacio_repository

    def crear(
        self,
        espacio_id: UUID,
        dia_semana: int,
        hora_apertura: time,
        hora_cierre: time,
        activa: bool = True,
    ) -> Disponibilidad:
        self._validar_datos(
            dia_semana,
            hora_apertura,
            hora_cierre,
        )

        espacio = self.espacio_repository.obtener_por_id(
            espacio_id
        )

        if espacio is None:
            raise ResourceNotFound("El espacio no existe.")

        disponibilidad = Disponibilidad(
            id=uuid4(),
            espacio_id=espacio_id,
            dia_semana=dia_semana,
            hora_apertura=hora_apertura,
            hora_cierre=hora_cierre,
            activa=activa,
        )

        return self.repository.crear(disponibilidad)

    def obtener(
        self,
        disponibilidad_id: UUID,
    ) -> Disponibilidad | None:
        return self.repository.obtener_por_id(
            disponibilidad_id
        )

    def listar(
        self,
        pagina: int,
        tamano: int,
        espacio_id: UUID | None = None,
        dia_semana: int | None = None,
        activa: bool | None = None,
    ) -> tuple[list[Disponibilidad], int]:
        if pagina < 1:
            raise ValueError(
                "La página debe ser mayor o igual a 1."
            )

        if tamano < 1 or tamano > 100:
            raise ValueError(
                "El tamaño debe estar entre 1 y 100."
            )

        if dia_semana is not None and not 0 <= dia_semana <= 6:
            raise ValueError(
                "El día debe estar entre 0 (lunes) y 6 (domingo)."
            )

        offset = (pagina - 1) * tamano

        disponibilidades = self.repository.listar(
            offset=offset,
            limite=tamano,
            espacio_id=espacio_id,
            dia_semana=dia_semana,
            activa=activa,
        )

        total = self.repository.contar(
            espacio_id=espacio_id,
            dia_semana=dia_semana,
            activa=activa,
        )

        return disponibilidades, total

    def actualizar(
        self,
        disponibilidad_id: UUID,
        espacio_id: UUID,
        dia_semana: int,
        hora_apertura: time,
        hora_cierre: time,
        activa: bool,
    ) -> Disponibilidad | None:
        actual = self.repository.obtener_por_id(
            disponibilidad_id
        )

        if actual is None:
            return None

        espacio = self.espacio_repository.obtener_por_id(
            espacio_id
        )

        if espacio is None:
            raise ResourceNotFound("El espacio no existe.")

        self._validar_datos(
            dia_semana,
            hora_apertura,
            hora_cierre,
        )

        actualizada = Disponibilidad(
            id=actual.id,
            espacio_id=espacio_id,
            dia_semana=dia_semana,
            hora_apertura=hora_apertura,
            hora_cierre=hora_cierre,
            activa=activa,
        )

        return self.repository.actualizar(actualizada)

    def eliminar(self, disponibilidad_id: UUID) -> bool:
        return self.repository.eliminar(disponibilidad_id)

    def _validar_datos(
        self,
        dia_semana: int,
        hora_apertura: time,
        hora_cierre: time,
    ) -> None:
        if not 0 <= dia_semana <= 6:
            raise ValueError(
                "El día debe estar entre 0 y 6."
            )

        if hora_apertura >= hora_cierre:
            raise ValueError(
                "La hora de cierre debe ser posterior "
                "a la hora de apertura."
            )
