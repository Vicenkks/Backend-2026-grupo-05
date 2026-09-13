from datetime import datetime

from app.domain.reservation import Reservation, ReservationStatus
from app.repositories.company_repository import CompanyRepositry
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.space_repository import SpaceRepository
from app.schemas.reservation import ReservationCreate, ReservationUpdate


class ReservationService:
	def __init__(
		self,
		reservation_repository: ReservationRepository,
		space_repository: SpaceRepository,
		company_repository: CompanyRepositry,
	) -> None:
		self.reservation_repository = reservation_repository
		self.space_repository = space_repository
		self.company_repository = company_repository

	def create(self, data: ReservationCreate) -> Reservation:
		space = self.space_repository.get_by_id(data.spaceId)
		if space is None:
			raise LookupError(f"Space '{data.spaceId}' was not found")
		if space.status.value != "active":
			raise ValueError("Reservations can only be created for active spaces")
		if self.company_repository.get_by_id(data.companyId) is None:
			raise LookupError(f"Company '{data.companyId}' was not found")
		self._ensure_no_conflicts(data.spaceId, data.companyId, data.start_date, data.end_date)
		reservation = Reservation.create(
			spaceId=data.spaceId,
			companyId=data.companyId,
			start_date=data.start_date,
			end_date=data.end_date,
			reason=data.reason,
			status=ReservationStatus(data.status.value),
		)
		return self.reservation_repository.add(reservation)

	def get_by_id(self, reservation_id: str) -> Reservation:
		reservation = self.reservation_repository.get_by_id(reservation_id)
		if reservation is None:
			raise LookupError(f"Reservation '{reservation_id}' was not found")
		return reservation

	def get_all(self) -> list[Reservation]:
		return self.reservation_repository.get_all()

	def update(self, reservation_id: str, data: ReservationUpdate) -> Reservation:
		reservation = self.get_by_id(reservation_id)
		space_id = data.spaceId or reservation.spaceId
		company_id = data.companyId or reservation.companyId
		start_date = data.start_date or reservation.start_date
		end_date = data.end_date or reservation.end_date
		space = self.space_repository.get_by_id(space_id)
		if space is None:
			raise LookupError(f"Space '{space_id}' was not found")
		if space.status.value != "active":
			raise ValueError("Reservations can only use active spaces")
		if self.company_repository.get_by_id(company_id) is None:
			raise LookupError(f"Company '{company_id}' was not found")
		self._ensure_no_conflicts(space_id, company_id, start_date, end_date, reservation_id)
		if end_date <= start_date:
			raise ValueError("End date must be later than start date")
		if (end_date - start_date).total_seconds() < 30 * 60:
			raise ValueError("Minimum duration must be 30 minutes")
		reservation.spaceId = space_id.strip()
		reservation.companyId = company_id.strip()
		reservation.start_date = start_date
		reservation.end_date = end_date
		if data.reason is not None:
			reservation.reason = data.reason.strip()
		if data.status is not None:
			reservation.status = ReservationStatus(data.status.value)
		reservation.updated_at = datetime.now()
		return reservation

	def delete(self, reservation_id: str) -> None:
		reservation = self.get_by_id(reservation_id)
		if not self.reservation_repository.delete(reservation):
			raise LookupError(f"Reservation '{reservation_id}' was not found")

	def _ensure_no_conflicts(
		self,
		space_id: str,
		company_id: str,
		start_date: datetime,
		end_date: datetime,
		excluded_reservation_id: str | None = None,
	) -> None:
		active_statuses = {ReservationStatus.PENDING, ReservationStatus.CONFIRMED}
		for reservation in self.reservation_repository.get_all():
			if reservation.reservationId == excluded_reservation_id:
				continue
			if reservation.status not in active_statuses:
				continue
			overlaps = start_date < reservation.end_date and end_date > reservation.start_date
			if not overlaps:
				continue
			if reservation.spaceId == space_id:
				raise ValueError("The space is already reserved for the requested period")
			if reservation.companyId == company_id:
				raise ValueError("The company already has a reservation for the requested period")
