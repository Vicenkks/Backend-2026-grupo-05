from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
from app.domain.validadores import validar_texto


@dataclass
class Empresa:
    idEmpresa: str
    nombreEmpresa: str
    rut: str
    email: str
    telefono: str
    direccion: str
    creado_en: datetime
    actualizado_en: datetime

    @classmethod
    def crear(cls, nombreEmpresa: str, rut: str, email: str, telefono: str, direccion: str) -> "Empresa":
        cls._validar_rut(rut)
        cls._validar_email(email)

        ahora = datetime.now()
        return cls(
            idEmpresa=str(uuid4()),
            nombreEmpresa=validar_texto(nombreEmpresa, "nombre de la empresa"),
            rut=rut.strip(),
            email=email.strip().lower(),
            telefono=telefono.strip(),
            direccion=validar_texto(direccion, "dirección"),
            creado_en=ahora,
            actualizado_en=ahora
        )

    @staticmethod
    def _validar_rut(rut: str) -> None:
        # Formato esperado: 12345678-9 (sin puntos)
        rut = rut.strip()
        if "-" not in rut:
            raise ValueError("El RUT debe contener un guión (-)")
        
        partes = rut.split("-")
        if len(partes) != 2:
            raise ValueError("Formato de RUT inválido")
        
        cuerpo = partes[0]
        dv = partes[1]
        
        if not cuerpo.isdigit() or len(cuerpo) < 7 or len(cuerpo) > 8:
            raise ValueError("El cuerpo del RUT debe tener 7 u 8 dígitos")
        
        if not dv or len(dv) > 1:
            raise ValueError("El dígito verificador es inválido")

    @staticmethod
    def _validar_email(email: str) -> None:
        email = email.strip()
        if not email or "@" not in email or "." not in email:
            raise ValueError("Email con formato inválido")
        if email.startswith("@") or email.startswith(".") or email.endswith("@") or email.endswith("."):
            raise ValueError("Email no puede comenzar o terminar con @ o .")
        if email.count("@") != 1:
            raise ValueError("El email debe tener un solo @")
        
        parte_local, dominio = email.split("@")
        if not parte_local or not dominio or "." not in dominio:
            raise ValueError("El dominio del email es inválido")

    def actualizar(self, nombreEmpresa: str = None, rut: str = None, email: str = None, telefono: str = None, direccion: str = None):
        if nombreEmpresa is not None:
            self.nombreEmpresa = validar_texto(nombreEmpresa, "nombre de la empresa")
        if rut is not None:
            self._validar_rut(rut)
            self.rut = rut.strip()
        if email is not None:
            self._validar_email(email)
            self.email = email.strip().lower()
        if telefono is not None:
            self.telefono = telefono.strip()
        if direccion is not None:
            self.direccion = validar_texto(direccion, "dirección")
        self.actualizado_en = datetime.now()