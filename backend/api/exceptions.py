import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from constants import system_messages as SYS_MSG
from domain.exceptions import (
    CategoryCycleError,
    CurrencyMismatchError,
    DomainError,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger("ledgerlens.api")

_DOMAIN_ERROR_STATUS: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    CurrencyMismatchError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    CategoryCycleError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def _error_envelope(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "statusCode": status_code,
            "message": message,
            "data": None,
            "meta": None,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registers every global exception handler, once, at app startup.

    Every response — success or failure — normalizes to the same envelope
    shape (TRD §5); this is the failure-path half of that guarantee.
    """

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        status_code = _DOMAIN_ERROR_STATUS.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return _error_envelope(status_code, str(exc) or SYS_MSG.VALIDATION_ERROR)

    # Registered on Starlette's base HTTPException, not fastapi.HTTPException:
    # framework-raised errors (404 route-not-found, 405) raise the Starlette
    # class directly, which wouldn't match a handler registered on the
    # fastapi subclass.
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _error_envelope(exc.status_code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, _exc: RequestValidationError
    ) -> JSONResponse:
        return _error_envelope(status.HTTP_422_UNPROCESSABLE_ENTITY, SYS_MSG.VALIDATION_ERROR)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # Full traceback (file/line) and timestamp go to the server log via
        # logger's own record metadata — never into the client-facing envelope,
        # which would otherwise leak internals to an API consumer.
        logger.exception(
            "Unhandled exception on %s %s", request.method, request.url.path, exc_info=exc
        )
        return _error_envelope(status.HTTP_500_INTERNAL_SERVER_ERROR, SYS_MSG.INTERNAL_ERROR)
