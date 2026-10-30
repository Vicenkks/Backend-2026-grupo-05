from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from domain.errors import ResourceNotFound, Conflict


def response(status, code, message, details=None):
    return JSONResponse(status_code=status, content=jsonable_encoder({
        "error": {"code": code, "message": str(message), "details": details or []}
    }))


def register_error_handlers(app):
    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException):
        codes = {400: "BUSINESS_RULE_VIOLATION", 404: "RESOURCE_NOT_FOUND", 409: "CONFLICT"}
        return response(error.status_code, codes.get(error.status_code, "HTTP_ERROR"), error.detail)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        details = [{"field": list(e["loc"]), "message": e["msg"], "type": e["type"]} for e in error.errors()]
        return response(422, "VALIDATION_ERROR", "Los datos no cumplen el esquema.", details)

    @app.exception_handler(ResourceNotFound)
    async def not_found(request: Request, error: ResourceNotFound):
        return response(404, "RESOURCE_NOT_FOUND", error)

    @app.exception_handler(Conflict)
    async def conflict(request: Request, error: Conflict):
        return response(409, "CONFLICT", error)

    @app.exception_handler(ValueError)
    async def business_error(request: Request, error: ValueError):
        return response(400, "BUSINESS_RULE_VIOLATION", error)

    @app.exception_handler(IntegrityError)
    async def integrity_error(request: Request, error: IntegrityError):
        return response(409, "CONFLICT", "La operación duplica datos o afecta recursos relacionados.")
