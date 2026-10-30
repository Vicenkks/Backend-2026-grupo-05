from domain.disponibilidad_domain import Disponibilidad
from infrastructure.models.disponibilidad_model import DisponibilidadModel

def a_domain(obj: DisponibilidadModel) -> Disponibilidad:
    return Disponibilidad(
        id=obj.id,
        espacio_id=obj.espacio_id,
        dia_semana=obj.dia_semana,
        hora_apertura=obj.hora_apertura,
        hora_cierre=obj.hora_cierre,
        activa=obj.activa,
    )

def a_model(obj: Disponibilidad) -> DisponibilidadModel:
    return DisponibilidadModel(
        id=obj.id,
        espacio_id=obj.espacio_id,
        dia_semana=obj.dia_semana,
        hora_apertura=obj.hora_apertura,
        hora_cierre=obj.hora_cierre,
        activa=obj.activa,
    )

def actualizar_model(modelo, entidad):
    modelo.espacio_id = entidad.espacio_id
    modelo.dia_semana = entidad.dia_semana
    modelo.hora_apertura = entidad.hora_apertura
    modelo.hora_cierre = entidad.hora_cierre
    modelo.activa = entidad.activa

actualizar_modelo = actualizar_model
