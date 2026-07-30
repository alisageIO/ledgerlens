from fastapi.testclient import TestClient


def test_unknown_route_returns_envelope_shaped_error(client: TestClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["statusCode"] == 404
    assert body["data"] is None
