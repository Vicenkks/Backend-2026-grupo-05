from domain.empresa_domain import Empresa
from infrastructure.models.empresa_model import EmpresaModel

def a_domain(obj: EmpresaModel) -> Empresa:
    return Empresa(
        id=obj.id,
        nombre=obj.nombre,
        rut=obj.rut,
        contacto=obj.contacto,
        activa=obj.activa,
    )

def a_model(obj: Empresa) -> EmpresaModel:
    return EmpresaModel(
        id=obj.id,
        nombre=obj.nombre,
        rut=obj.rut,
        contacto=obj.contacto,
        activa=obj.activa,
    )

def actualizar_model(modelo, entidad):
    modelo.nombre = entidad.nombre
    modelo.rut = entidad.rut
    modelo.contacto = entidad.contacto
    modelo.activa = entidad.activa

actualizar_modelo = actualizar_model
