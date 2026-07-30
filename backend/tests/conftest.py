from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.main import app
from config.database import SessionLocal, engine
from domain.shared.base import Base


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Iterator[Session]:
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()
