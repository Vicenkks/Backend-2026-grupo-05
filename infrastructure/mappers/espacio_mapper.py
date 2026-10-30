
from domain.espacio_domain import Espacio, TipoEspacio, EstadoEspacio
from infrastructure.models.espacio_model import EspacioModel


def a_dominio(modelo: EspacioModel) -> Espacio:
    return Espacio(
        id=modelo.id,
        nombre=modelo.nombre,
        tipo=TipoEspacio(modelo.tipo),
        capacidad=modelo.capacidad,
        estado=EstadoEspacio(modelo.estado),
    )


def a_modelo(espacio: Espacio) -> EspacioModel:
    return EspacioModel(
        id=espacio.id,
        nombre=espacio.nombre,
        tipo=espacio.tipo.value,
        capacidad=espacio.capacidad,
        estado=espacio.estado.value,
    )


def actualizar_modelo(modelo: EspacioModel, espacio: Espacio) -> None:
    modelo.nombre = espacio.nombre
    modelo.tipo = espacio.tipo.value
    modelo.capacidad = espacio.capacidad
    modelo.estado = espacio.estado.value
