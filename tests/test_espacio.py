from datetime import time

import pytest

from app.domain.availability import Availability, Weekday


def test_create_availability_with_valid_data():
    availability = Availability.create(
        spaceId="space-1",
        weekday=Weekday.MONDAY,
        opening_time=time(9, 0),
        closing_time=time(18, 0),
    )

    assert availability.spaceId == "space-1"
    assert availability.weekday == Weekday.MONDAY
    assert availability.opening_time == time(9, 0)
    assert availability.closing_time == time(18, 0)
    assert availability.availabilityId is not None


def test_create_availability_with_closing_before_opening_raises_error():
    with pytest.raises(ValueError):
        Availability.create(
            spaceId="space-1",
            weekday=Weekday.MONDAY,
            opening_time=time(18, 0),
            closing_time=time(9, 0),
        )


def test_create_availability_with_equal_times_raises_error():
    with pytest.raises(ValueError):
        Availability.create(
            spaceId="space-1",
            weekday=Weekday.MONDAY,
            opening_time=time(9, 0),
            closing_time=time(9, 0),
        )


def test_update_schedule_changes_times():
    availability = Availability.create(
        spaceId="space-1",
        weekday=Weekday.MONDAY,
        opening_time=time(9, 0),
        closing_time=time(18, 0),
    )
    original_updated_at = availability.updated_at

    availability.update_schedule(opening_time=time(8, 0), closing_time=time(20, 0))

    assert availability.opening_time == time(8, 0)
    assert availability.closing_time == time(20, 0)
    assert availability.updated_at >= original_updated_at


def test_update_schedule_with_invalid_result_raises_error():
    availability = Availability.create(
        spaceId="space-1",
        weekday=Weekday.MONDAY,
        opening_time=time(9, 0),
        closing_time=time(18, 0),
    )

    with pytest.raises(ValueError):
        availability.update_schedule(opening_time=time(19, 0))


def test_update_schedule_with_partial_update_keeps_other_value():
    availability = Availability.create(
        spaceId="space-1",
        weekday=Weekday.MONDAY,
        opening_time=time(9, 0),
        closing_time=time(18, 0),
    )

    availability.update_schedule(closing_time=time(20, 0))

    assert availability.opening_time == time(9, 0)
    assert availability.closing_time == time(20, 0)
