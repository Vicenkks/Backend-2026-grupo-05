from domain.errors import ResourceNotFound, Conflict

from datetime import datetime, timezone
from uuid import UUID, uuid4

from domain.reserva_domain import Reserva, EstadoReserva
from infrastructure.repositories.reserva_repository import (
    ReservaRepository,
)
from infrastructure.repositories.espacio_repository import (
    EspacioRepository,
)
from infrastructure.repositories.empresa_repository import (
    EmpresaRepository,
)
from infrastructure.repositories.disponibilidad_repository import (
    DisponibilidadRepository,
)


class ReservaService:
    def __init__(
        self,
        repository: ReservaRepository,
        espacio_repository: EspacioRepository,
        empresa_repository: EmpresaRepository,
        disponibilidad_repository: DisponibilidadRepository,
    ) -> None:
        self.repository = repository
        self.espacio_repository = espacio_repository
        self.empresa_repository = empresa_repository
        self.disponibilidad_repository = disponibilidad_repository

    def crear(
        self,
        espacio_id: UUID,
        empresa_id: UUID,
        fecha_inicio: datetime,
        fecha_fin: datetime,
    ) -> Reserva:
        self._validar_fechas(fecha_inicio, fecha_fin)
        fecha_inicio = fecha_inicio.astimezone(timezone.utc)
        fecha_fin = fecha_fin.astimezone(timezone.utc)

        espacio = self.espacio_repository.obtener_por_id(
            espacio_id
        )

        if espacio is None:
            raise ResourceNotFound("El espacio no existe.")

        if espacio.estado != "activo":
            raise ValueError(
                "El espacio no está activo."
            )

        empresa = self.empresa_repository.obtener_por_id(
            empresa_id
        )

        if empresa is None:
            raise ResourceNotFound("La empresa no existe.")

        if not empresa.activa:
            raise ValueError("La empresa no está activa.")

        self._validar_disponibilidad(
            espacio_id,
            fecha_inicio,
            fecha_fin,
        )

        if self.repository.existe_solapamiento_espacio(
            espacio_id=espacio_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        ):
            raise Conflict(
                "El espacio ya tiene una reserva en ese horario."
            )

        if self.repository.existe_solapamiento_empresa(
            empresa_id=empresa_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        ):
            raise Conflict(
                "La empresa ya tiene una reserva en ese horario."
            )

        reserva = Reserva(
            id=uuid4(),
            espacio_id=espacio_id,
            empresa_id=empresa_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado=EstadoReserva.CONFIRMADA,
        )

        return self.repository.crear(reserva)

    def obtener(self, reserva_id: UUID) -> Reserva | None:
        return self.repository.obtener_por_id(reserva_id)

    def listar(
        self,
        pagina: int,
        tamano: int,
        espacio_id: UUID | None = None,
        empresa_id: UUID | None = None,
        estado: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> tuple[list[Reserva], int]:
        if pagina < 1:
            raise ValueError(
                "La página debe ser mayor o igual a 1."
            )

        if tamano < 1 or tamano > 100:
            raise ValueError(
                "El tamaño debe estar entre 1 y 100."
            )

        offset = (pagina - 1) * tamano

        reservas = self.repository.listar(
            offset=offset,
            limite=tamano,
            espacio_id=espacio_id,
            empresa_id=empresa_id,
            estado=estado,
            desde=desde,
            hasta=hasta,
        )

        total = self.repository.contar(
            espacio_id=espacio_id,
            empresa_id=empresa_id,
            estado=estado,
            desde=desde,
            hasta=hasta,
        )

        return reservas, total

    def cancelar(self, reserva_id: UUID) -> Reserva | None:
        reserva = self.repository.obtener_por_id(reserva_id)

        if reserva is None:
            return None

        if reserva.estado == EstadoReserva.CANCELADA:
            raise Conflict("La reserva ya está cancelada.")

        if reserva.fecha_inicio <= datetime.now(
            tz=reserva.fecha_inicio.tzinfo
        ):
            raise ValueError(
                "No se puede cancelar una reserva "
                "que ya comenzó."
            )

        reserva.estado = EstadoReserva.CANCELADA

        return self.repository.actualizar(reserva)

    def _validar_fechas(
        self,
        fecha_inicio: datetime,
        fecha_fin: datetime,
    ) -> None:
        if fecha_inicio.tzinfo is None or fecha_fin.tzinfo is None:
            raise ValueError("Las fechas deben incluir zona horaria.")

        if fecha_fin <= fecha_inicio:
            raise ValueError(
                "La fecha de fin debe ser posterior al inicio."
            )

        if (fecha_fin - fecha_inicio).total_seconds() < 1800:
            raise ValueError(
                "La reserva debe durar al menos 30 minutos."
            )

        if (
            fecha_inicio.tzinfo is None
        ) != (
            fecha_fin.tzinfo is None
        ):
            raise ValueError(
                "Las fechas deben usar el mismo criterio "
                "de zona horaria."
            )

    def _validar_disponibilidad(
        self,
        espacio_id: UUID,
        fecha_inicio: datetime,
        fecha_fin: datetime,
    ) -> None:
        # Una reserva debe comenzar y terminar el mismo día
        # en esta primera versión.
        if fecha_inicio.date() != fecha_fin.date():
            raise ValueError(
                "La reserva debe comenzar y terminar el mismo día."
            )

        dia_semana = fecha_inicio.weekday()

        disponibilidades = self.disponibilidad_repository.listar(
            offset=0,
            limite=100,
            espacio_id=espacio_id,
            dia_semana=dia_semana,
            activa=True,
        )

        dentro_del_horario = any(
            disponibilidad.hora_apertura <= fecha_inicio.time()
            and fecha_fin.time() <= disponibilidad.hora_cierre
            for disponibilidad in disponibilidades
        )

        if not dentro_del_horario:
            raise ValueError(
                "La reserva está fuera del horario disponible."
            )
