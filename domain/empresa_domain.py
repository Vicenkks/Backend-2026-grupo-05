from dataclasses import dataclass
from uuid import UUID


def validar_rut(rut: str) -> bool:
    rut = rut.upper().replace(".", "").replace("-", "").replace(" ", "")

    if len(rut) < 2:
        return False

    cuerpo, dv = rut[:-1], rut[-1]

    if not cuerpo.isdigit():
        return False

    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = 11 - (suma % 11)

    if resto == 11:
        esperado = "0"
    elif resto == 10:
        esperado = "K"
    else:
        esperado = str(resto)

    return dv == esperado


@dataclass
class Empresa:
    id: UUID
    nombre: str
    rut: str
    contacto: str
    activa: bool = True

    def __post_init__(self):
        if not self.nombre.strip():
            raise ValueError("El nombre de la empresa es obligatorio")

        if not validar_rut(self.rut):
            raise ValueError("El RUT no es válido")

        if not self.contacto.strip():
            raise ValueError("El contacto es obligatorio")

    def puede_reservar(self) -> bool:
        return self.activa

    def desactivar(self):
        self.activa = False
