import logging

from fastapi import FastAPI

from api.envelope import EnvelopeRoute
from api.exceptions import register_exception_handlers
from api.routes import health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

app = FastAPI(title="LedgerLens API")
app.router.route_class = EnvelopeRoute

register_exception_handlers(app)

app.include_router(health.router)
