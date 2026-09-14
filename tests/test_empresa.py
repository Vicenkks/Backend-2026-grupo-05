import pytest

from app.domain.company import Company


def test_create_company_with_valid_data():
    company = Company.create(
        companyName="Acme Ltda",
        rut="12345678-9",
        email="Contacto@Acme.cl",
        phone="+56912345678",
        address="Av. Siempre Viva 123",
    )

    assert company.companyName == "Acme Ltda"
    assert company.rut == "12345678-9"
    assert company.email == "contacto@acme.cl"  # se normaliza a minúsculas
    assert company.companyId is not None


@pytest.mark.parametrize(
    "invalid_rut",
    [
        "123456789",       # sin guion
        "1234567-8-9",     # más de un guion
        "abc-9",           # cuerpo no numérico
        "123-9",           # cuerpo muy corto
        "123456789012-9",  # cuerpo muy largo
        "12345678-",       # sin dígito verificador
    ],
)
def test_create_company_with_invalid_rut_raises_error(invalid_rut):
    with pytest.raises(ValueError):
        Company.create(
            companyName="Acme Ltda",
            rut=invalid_rut,
            email="contacto@acme.cl",
            phone="+56912345678",
            address="Av. Siempre Viva 123",
        )


@pytest.mark.parametrize(
    "invalid_email",
    [
        "sin-arroba.cl",
        "@sinusuario.cl",
        "usuario@",
        "usuario@dominio",   # sin punto en el dominio
        "usuario@@dominio.cl",
    ],
)
def test_create_company_with_invalid_email_raises_error(invalid_email):
    with pytest.raises(ValueError):
        Company.create(
            companyName="Acme Ltda",
            rut="12345678-9",
            email=invalid_email,
            phone="+56912345678",
            address="Av. Siempre Viva 123",
        )


def test_create_company_with_empty_name_raises_error():
    with pytest.raises(ValueError):
        Company.create(
            companyName="   ",
            rut="12345678-9",
            email="contacto@acme.cl",
            phone="+56912345678",
            address="Av. Siempre Viva 123",
        )


def test_update_company_changes_fields():
    company = Company.create(
        companyName="Acme Ltda",
        rut="12345678-9",
        email="contacto@acme.cl",
        phone="+56912345678",
        address="Av. Siempre Viva 123",
    )
    original_updated_at = company.updated_at

    company.update(companyName="Acme SPA", phone="+56900000000")

    assert company.companyName == "Acme SPA"
    assert company.phone == "+56900000000"
    assert company.updated_at >= original_updated_at


def test_update_company_with_invalid_email_raises_error():
    company = Company.create(
        companyName="Acme Ltda",
        rut="12345678-9",
        email="contacto@acme.cl",
        phone="+56912345678",
        address="Av. Siempre Viva 123",
    )

    with pytest.raises(ValueError):
        company.update(email="correo-invalido")
