from fastapi.testclient import TestClient

from api.main import app
from config.database import get_db
from constants import system_messages as SYS_MSG


class _FakeSession:
    def execute(self, _statement: object) -> None:
        return None


def _override_get_db() -> object:
    return _FakeSession()


def test_health_returns_envelope_shaped_success(client: TestClient) -> None:
    app.dependency_overrides[get_db] = _override_get_db
    try:
        response = client.get("/health")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["statusCode"] == 200
    assert body["data"] == {"status": SYS_MSG.HEALTHY}
    assert body["meta"] is None
