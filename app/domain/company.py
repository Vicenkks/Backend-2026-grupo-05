from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
from app.domain.validators import validate_text

@dataclass
class Company:
    companyId: str
    companyName: str
    rut: str
    email: str
    phone: str
    address: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, companyName: str, rut: str, email: str, phone: str, address: str) -> "Company":
        cls._validate_rut(rut)
        cls._validate_email(email)
        now = datetime.now()
        return cls(
            companyId=str(uuid4()),
            companyName=validate_text(companyName, "company name"),
            rut=rut.strip(),
            email=email.strip().lower(),
            phone=phone.strip(),
            address=validate_text(address, "address"),
            created_at=now,
            updated_at=now
        )

    @staticmethod
    def _validate_rut(rut: str) -> None:
        # Expected format: 12345678-9 (no dots)
        rut = rut.strip()
        if "-" not in rut:
            raise ValueError("RUT must contain a hyphen (-)")
        parts = rut.split("-")
        if len(parts) != 2:
            raise ValueError("Invalid RUT format")
        body = parts[0]
        dv = parts[1]
        if not body.isdigit() or len(body) < 7 or len(body) > 8:
            raise ValueError("RUT body must have 7 or 8 digits")
        if not dv or len(dv) > 1:
            raise ValueError("Invalid verification digit")

    @staticmethod
    def _validate_email(email: str) -> None:
        email = email.strip()
        if not email or "@" not in email or "." not in email:
            raise ValueError("Invalid email format")
        if email.startswith("@") or email.startswith(".") or email.endswith("@") or email.endswith("."):
            raise ValueError("Email cannot start or end with @ or .")
        if email.count("@") != 1:
            raise ValueError("Email must have only one @")
        local_part, domain = email.split("@")
        if not local_part or not domain or "." not in domain:
            raise ValueError("Invalid email domain")

    def update(self, companyName: str = None, rut: str = None, email: str = None, phone: str = None, address: str = None):
        if companyName is not None:
            self.companyName = validate_text(companyName, "company name")
        if rut is not None:
            self._validate_rut(rut)
            self.rut = rut.strip()
        if email is not None:
            self._validate_email(email)
            self.email = email.strip().lower()
        if phone is not None:
            self.phone = phone.strip()
        if address is not None:
            self.address = validate_text(address, "address")
        self.updated_at = datetime.now()