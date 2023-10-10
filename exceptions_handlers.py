from starlette.requests import Request
from starlette.responses import JSONResponse

from app import app
from repositories.exceptions import DoesNotExistException


@app.exception_handler(DoesNotExistException)
async def unicorn_exception_handler(request: Request, exc: DoesNotExistException):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )
