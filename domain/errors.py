class DomainError(Exception):
    pass

class ResourceNotFound(DomainError):
    pass

class Conflict(DomainError):
    pass
