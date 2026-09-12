from app.domain.company import Company

class CompanyRepositry:
    def __init__(self):
        self.companies: dict[str, Company] = {}
    def add(self, company: Company) -> Company:
        self.companies[company.companyId] = company
        return company
    def get_by_id(self, companyId:str) ->Company | None:
        return self.companies.get(companyId)
    def delete(self, company: Company) -> bool:
        return self.companies.pop(company.companyId, None) is not None

    def get_all(self) -> list[Company]:
        return list(self.companies.values())