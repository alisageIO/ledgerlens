import json
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from constants import system_messages as SYS_MSG


class Envelope[T](BaseModel):
    """The single response shape every endpoint returns (TRD §5)."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    success: bool
    status_code: int
    message: str
    data: T | None = None
    meta: dict[str, Any] | None = None


class EnvelopeRoute(APIRoute):
    """Wraps every successful JSON response body in the envelope shape.

    Registered once via ``app.router.route_class = EnvelopeRoute``. Route
    handlers keep returning plain, typed data (``response_model=SomeOut``) —
    this is the one place that data actually gets wrapped into
    ``{success, statusCode, message, data, meta}``. Error responses are
    wrapped separately by the exception handlers in api/exceptions.py, since
    by the time a raised exception reaches here it's already left this
    handler's try block.
    """

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def envelope_route_handler(request: Request) -> Response:
            response = await original_route_handler(request)
            if not isinstance(response, JSONResponse) or response.status_code >= 400:
                return response

            envelope = Envelope[Any](
                success=True,
                status_code=response.status_code,
                message=SYS_MSG.OPERATION_SUCCESSFUL,
                data=json.loads(bytes(response.body)),
            )
            return JSONResponse(
                content=envelope.model_dump(by_alias=True),
                status_code=response.status_code,
            )

        return envelope_route_handler
