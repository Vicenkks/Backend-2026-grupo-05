import pytest

from app.domain.company import Company


def test_create_company_valid():
    company = Company.create(
        companyName="Acme Ltda",
        rut="12345678-9",
        email="contacto@acme.cl",
        phone="+56912345678",
        address="Av. Siempre Viva 123",
    )

    assert company.companyName == "Acme Ltda"
    assert company.rut == "12345678-9"


def test_create_company_invalid_rut_raises_error():
    with pytest.raises(ValueError):
        Company.create(
            companyName="Acme Ltda",
            rut="123456789",  # sin guion
            email="contacto@acme.cl",
            phone="+56912345678",
            address="Av. Siempre Viva 123",
        )


def test_create_company_invalid_email_raises_error():
    with pytest.raises(ValueError):
        Company.create(
            companyName="Acme Ltda",
            rut="12345678-9",
            email="correo-invalido",
            phone="+56912345678",
            address="Av. Siempre Viva 123",
        )
