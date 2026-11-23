"""Reglas de negocio: límites, estados, horarios y cancelación."""

from datetime import UTC, datetime, time, timedelta
from uuid import uuid4

import pytest

from domain.disponibilidad_domain import Disponibilidad
from domain.empresa_domain import Empresa, validar_rut
from domain.espacio_domain import Espacio, EstadoEspacio, TipoEspacio
from domain.reserva_domain import EstadoReserva, Reserva

pytestmark = pytest.mark.unit
START = datetime(2035, 1, 8, 10, tzinfo=UTC)


@pytest.mark.parametrize(
    ("rut", "valid"),
    [
        ("", False),
        ("ABC-K", False),
        ("11111111-1", True),
        ("6.000.000-K", True),
        ("00000000-0", True),
        ("11111111-2", False),
    ],
)
def test_rut(rut, valid):
    assert validar_rut(rut) is valid


def test_company_states():
    company = Empresa(uuid4(), "Empresa", "11111111-1", "test@example.com")
    assert company.puede_reservar()
    company.desactivar()
    assert not company.puede_reservar()


@pytest.mark.parametrize(
    "overrides", [{"nombre": " "}, {"rut": "invalid"}, {"contacto": " "}]
)
def test_invalid_company(overrides):
    with pytest.raises(ValueError):
        Empresa(
            **{
                "id": uuid4(),
                "nombre": "Empresa",
                "rut": "11111111-1",
                "contacto": "test@example.com",
                **overrides,
            }
        )


def test_space_states():
    space = Espacio(uuid4(), "Sala", TipoEspacio.OFICINA, 2)
    assert space.esta_disponible_para_reserva()
    space.cambiar_estado(EstadoEspacio.MANTENIMIENTO)
    assert not space.esta_disponible_para_reserva()


@pytest.mark.parametrize("overrides", [{"nombre": " "}, {"capacidad": 0}])
def test_invalid_space(overrides):
    with pytest.raises(ValueError):
        Espacio(
            **{
                "id": uuid4(),
                "nombre": "Sala",
                "tipo": TipoEspacio.OFICINA,
                "capacidad": 2,
                **overrides,
            }
        )


@pytest.mark.parametrize(
    "overrides", [{"dia_semana": -1}, {"dia_semana": 7}, {"hora_cierre": time(8)}]
)
def test_invalid_availability(overrides):
    with pytest.raises(ValueError):
        Disponibilidad(
            **{
                "id": uuid4(),
                "espacio_id": uuid4(),
                "dia_semana": 0,
                "hora_apertura": time(9),
                "hora_cierre": time(18),
                **overrides,
            }
        )


@pytest.mark.parametrize(
    ("active", "start", "end", "expected"),
    [
        (True, START, START + timedelta(hours=1), True),
        (False, START, START + timedelta(hours=1), False),
        (True, START, START + timedelta(days=1), False),
        (True, START + timedelta(days=1), START + timedelta(days=1, hours=1), False),
        (True, START.replace(hour=8), START, False),
        (True, START, START.replace(hour=19), False),
    ],
)
def test_availability_contains(active, start, end, expected):
    availability = Disponibilidad(uuid4(), uuid4(), 0, time(9), time(18), active)
    assert availability.contiene(start, end) is expected


def booking(start=START, end=None):
    return Reserva(uuid4(), uuid4(), uuid4(), start, end or start + timedelta(hours=1))


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (START.replace(tzinfo=None), START),
        (START, START.replace(tzinfo=None)),
        (START, START),
        (START, START + timedelta(minutes=29)),
    ],
)
def test_invalid_reservation_dates(start, end):
    with pytest.raises(ValueError):
        booking(start, end)


def test_adjacent_reservations_do_not_overlap():
    first = booking()
    assert first.se_superpone_con(booking(START + timedelta(minutes=30)))
    assert not first.se_superpone_con(booking(START + timedelta(hours=1)))


def test_reservation_cancellation():
    reservation = booking()
    assert reservation.ocupa_espacio()
    reservation.cancelar(START - timedelta(seconds=1))
    assert reservation.estado == EstadoReserva.CANCELADA
    assert not reservation.ocupa_espacio()
    with pytest.raises(ValueError):
        reservation.cancelar(START - timedelta(seconds=1))


@pytest.mark.parametrize(
    "current", [START, START + timedelta(seconds=1), START.replace(tzinfo=None)]
)
def test_cannot_cancel_started_or_naive(current):
    with pytest.raises(ValueError):
        booking().cancelar(current)
