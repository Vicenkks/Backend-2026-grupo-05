import pytest

from app.domain.space import Space


def test_create_space_valid():
    space = Space.create(
        spaceName="Sala Informatica",
        type="meeting_room",
        capacity=10,
        description="Sala con pcs",
    )

    assert space.spaceName == "Sala Informatica"
    assert space.capacity == 10


def test_create_space_invalid_capacity_raises_error():
    with pytest.raises(ValueError):
        Space.create(spaceName="Sala Informatica", type="office", capacity=0, description="Sala con pcs")


def test_update_space_changes_fields():
    space = Space.create(spaceName="Sala Informatica", type="office", capacity=5, description="Sala con pcs")

    space.update(spaceName="Sala Renovada", capacity=20)

    assert space.spaceName == "Sala Renovada"
    assert space.capacity == 20
    
