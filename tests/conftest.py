import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.instances import (
    availability_repository,
    company_repository,
    reservation_repository,
    space_repository,
)


@pytest.fixture
def client():
    space_repository.spaces.clear()
    company_repository.companies.clear()
    reservation_repository.reservations.clear()
    availability_repository.availabilities.clear()
    return TestClient(app)
