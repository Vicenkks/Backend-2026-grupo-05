from app.domain.reservation import Reservation

class ReservationRepository:
    def __init__(self):
        self.reservations: dict[str, Reservation] = {}

    def add(self,reservation: Reservation)-> Reservation:
        self.reservations[reservation.reservationId] = reservation
        return reservation

    def get_by_id(self, reservationId:str) -> Reservation| None:
        return self.reservations.get(reservationId)

    def get_all(self) -> list[Reservation]:
        return list(self.reservations.values())

    def delete(self, reservation:Reservation) -> bool:
        return self.reservations.pop(reservation.reservationId, None) is not None

    