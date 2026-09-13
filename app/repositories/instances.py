from app.repositories.availability_repository import AvailabilityRepository
from app.repositories.company_repository import CompanyRepositry
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.space_repository import SpaceRepository

space_repository = SpaceRepository()
company_repository = CompanyRepositry()
reservation_repository = ReservationRepository()
availability_repository = AvailabilityRepository()
