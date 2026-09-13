from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import availabilities, companies, reservations, spaces

app = FastAPI(title="Coworking Reservation API", version="1.0.0")
app.include_router(spaces.router)
app.include_router(companies.router)
app.include_router(reservations.router)
app.include_router(availabilities.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, error: HTTPException):
	detail = error.detail
	if isinstance(detail, dict) and "code" in detail:
		payload = detail
	else:
		payload = {
			"code": "HTTP_ERROR",
			"message": str(detail),
			"details": [],
		}
	return JSONResponse(status_code=error.status_code, content={"error": payload})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, error: RequestValidationError):
	details = [
		{"field": ".".join(str(part) for part in item["loc"]), "message": item["msg"]}
		for item in error.errors()
	]
	return JSONResponse(
		status_code=422,
		content={
			"error": {
				"code": "VALIDATION_ERROR",
				"message": "The request data is invalid",
				"details": details,
			}
		},
	)


@app.get("/", tags=["Health"])
def health_check():
	return {"status": "ok", "service": "Coworking Reservation API"}
