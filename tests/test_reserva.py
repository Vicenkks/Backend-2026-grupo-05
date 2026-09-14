from datetime import datetime, timedelta

import pytest

from app.domain.reservation import Reservation, ReservationStatus


def make_dates(duration_minutes=60):
    start = datetime(2026, 9, 15, 10, 0)
    end = start + timedelta(minutes=duration_minutes)
    return start, end


def test_create_reservation_with_valid_data():
    start, end = make_dates(60)

    reservation = Reservation.create(
        spaceId="space-1",
        companyId="company-1",
        start_date=start,
        end_date=end,
        reason="Reunión de planificación",
    )

    assert reservation.status == ReservationStatus.PENDING
    assert reservation.spaceId == "space-1"
    assert reservation.companyId == "company-1"
    assert reservation.reservationId is not None


def test_create_reservation_with_end_before_start_raises_error():
    start, _ = make_dates()
    end = start - timedelta(hours=1)

    with pytest.raises(ValueError):
        Reservation.create(
            spaceId="space-1",
            companyId="company-1",
            start_date=start,
            end_date=end,
            reason="Reunión",
        )


def test_create_reservation_with_end_equal_start_raises_error():
    start, _ = make_dates()

    with pytest.raises(ValueError):
        Reservation.create(
            spaceId="space-1",
            companyId="company-1",
            start_date=start,
            end_date=start,
            reason="Reunión",
        )


def test_create_reservation_shorter_than_30_minutes_raises_error():
    start, end = make_dates(29)

    with pytest.raises(ValueError):
        Reservation.create(
            spaceId="space-1",
            companyId="company-1",
            start_date=start,
            end_date=end,
            reason="Reunión",
        )


def test_create_reservation_with_exactly_30_minutes_is_valid():
    start, end = make_dates(30)

    reservation = Reservation.create(
        spaceId="space-1",
        companyId="company-1",
        start_date=start,
        end_date=end,
        reason="Reunión",
    )

    assert reservation.status == ReservationStatus.PENDING


def test_confirm_pending_reservation():
    start, end = make_dates()
    reservation = Reservation.create("space-1", "company-1", start, end, "Reunión")

    reservation.confirm()

    assert reservation.status == ReservationStatus.CONFIRMED


def test_confirm_non_pending_reservation_raises_error():
    start, end = make_dates()
    reservation = Reservation.create("space-1", "company-1", start, end, "Reunión")
    reservation.confirm()

    with pytest.raises(ValueError):
        reservation.confirm()


def test_cancel_pending_reservation():
    start, end = make_dates()
    reservation = Reservation.create("space-1", "company-1", start, end, "Reunión")

    reservation.cancel()

    assert reservation.status == ReservationStatus.CANCELED


def test_cancel_already_canceled_reservation_raises_error():
    start, end = make_dates()
    reservation = Reservation.create("space-1", "company-1", start, end, "Reunión")
    reservation.cancel()

    with pytest.raises(ValueError):
        reservation.cancel()


def test_cancel_completed_reservation_raises_error():
    start, end = make_dates()
    reservation = Reservation.create("space-1", "company-1", start, end, "Reunión")
    reservation.status = ReservationStatus.COMPLETED

    with pytest.raises(ValueError):
        reservation.cancel()
