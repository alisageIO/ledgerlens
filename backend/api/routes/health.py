from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.envelope import EnvelopeRoute
from config.database import get_db
from constants import system_messages as SYS_MSG

router = APIRouter(tags=["health"], route_class=EnvelopeRoute)


@router.get("/health")
def get_health(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    """Liveness/readiness probe — confirms the API can reach Postgres (TRD §8)."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=SYS_MSG.UNHEALTHY
        ) from exc
    return {"status": SYS_MSG.HEALTHY}
