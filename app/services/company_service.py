from app.domain.company import Company
from app.repositories.company_repository import CompanyRepositry
from app.schemas.company import CompanyCreate, CompanyUpdate


class CompanyService:
	def __init__(self, company_repository: CompanyRepositry) -> None:
		self.company_repository = company_repository

	def create(self, data: CompanyCreate) -> Company:
		company = Company.create(
			companyName=data.companyName,
			rut=data.rut,
			email=str(data.email),
			phone=data.phone,
			address=data.address,
		)
		return self.company_repository.add(company)

	def get_by_id(self, company_id: str) -> Company:
		company = self.company_repository.get_by_id(company_id)
		if company is None:
			raise LookupError(f"Company '{company_id}' was not found")
		return company

	def get_all(self) -> list[Company]:
		return self.company_repository.get_all()

	def update(self, company_id: str, data: CompanyUpdate) -> Company:
		company = self.get_by_id(company_id)
		company.update(
			companyName=data.companyName,
			rut=data.rut,
			email=str(data.email) if data.email is not None else None,
			phone=data.phone,
			address=data.address,
		)
		return company

	def delete(self, company_id: str) -> None:
		company = self.get_by_id(company_id)
		if not self.company_repository.delete(company):
			raise LookupError(f"Company '{company_id}' was not found")
