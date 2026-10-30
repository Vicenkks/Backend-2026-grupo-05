from domain.reserva_domain import Reserva
from infrastructure.models.reserva_model import ReservaModel

from datetime import timezone

def _utc(value):
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

def a_domain(obj: ReservaModel) -> Reserva:
    return Reserva(
        id=obj.id,
        espacio_id=obj.espacio_id,
        empresa_id=obj.empresa_id,
        fecha_inicio=_utc(obj.fecha_inicio),
        fecha_fin=_utc(obj.fecha_fin),
        estado=obj.estado,
    )

def a_model(obj: Reserva) -> ReservaModel:
    return ReservaModel(
        id=obj.id,
        espacio_id=obj.espacio_id,
        empresa_id=obj.empresa_id,
        fecha_inicio=obj.fecha_inicio,
        fecha_fin=obj.fecha_fin,
        estado=obj.estado,
    )

def actualizar_model(modelo, entidad):
    modelo.espacio_id = entidad.espacio_id
    modelo.empresa_id = entidad.empresa_id
    modelo.fecha_inicio = entidad.fecha_inicio
    modelo.fecha_fin = entidad.fecha_fin
    modelo.estado = entidad.estado

actualizar_modelo = actualizar_model
