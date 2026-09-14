import pytest

from app.domain.space import Space, SpaceStatus


def test_create_space_with_valid_data():
    space = Space.create(
        spaceName="Sala Innovación",
        type="meeting_room",
        capacity=10,
        description="Sala equipada con pizarra y proyector",
    )

    assert space.spaceName == "Sala Innovación"
    assert space.type == "meeting_room"
    assert space.capacity == 10
    assert space.status == SpaceStatus.ACTIVE
    assert space.spaceId is not None
    assert space.created_at == space.updated_at


def test_create_space_normalizes_type_to_lowercase():
    space = Space.create(
        spaceName="Sala 1",
        type="  MEETING_ROOM  ",
        capacity=5,
        description="desc",
    )

    assert space.type == "meeting_room"


def test_create_space_with_zero_capacity_raises_error():
    with pytest.raises(ValueError):
        Space.create(spaceName="Sala 1", type="office", capacity=0, description="desc")


def test_create_space_with_negative_capacity_raises_error():
    with pytest.raises(ValueError):
        Space.create(spaceName="Sala 1", type="office", capacity=-5, description="desc")


def test_create_space_with_empty_name_raises_error():
    with pytest.raises(ValueError):
        Space.create(spaceName="   ", type="office", capacity=5, description="desc")


def test_update_space_changes_fields_and_updated_at():
    space = Space.create(spaceName="Sala 1", type="office", capacity=5, description="desc")
    original_updated_at = space.updated_at

    space.update(spaceName="Sala Renovada", capacity=20, status=SpaceStatus.MAINTENANCE)

    assert space.spaceName == "Sala Renovada"
    assert space.capacity == 20
    assert space.status == SpaceStatus.MAINTENANCE
    assert space.updated_at >= original_updated_at


def test_update_space_with_invalid_capacity_raises_error():
    space = Space.create(spaceName="Sala 1", type="office", capacity=5, description="desc")

    with pytest.raises(ValueError):
        space.update(capacity=0)


def test_update_space_with_no_changes_keeps_existing_values():
    space = Space.create(spaceName="Sala 1", type="office", capacity=5, description="desc")

    space.update()

    assert space.spaceName == "Sala 1"
    assert space.capacity == 5
