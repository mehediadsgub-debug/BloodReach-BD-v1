from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


class DuplicateResourceError(Exception):
    """Raised when attempting to create a resource that already exists (e.g. duplicate email)."""


class ResourceNotFoundError(Exception):
    """Raised when a requested resource does not exist."""
