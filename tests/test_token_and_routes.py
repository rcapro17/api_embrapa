# tests/test_token_and_routes.py

import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def tokens(client):
    response = client.get("/token")
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"]
    }


def test_get_token(client):
    response = client.get("/token")
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.parametrize("endpoint", [
    "/api/producao",
    "/api/processamento",
    "/api/comercializacao",
    "/api/importacao",
    "/api/exportacao"
])
def test_protected_routes_require_token(client, endpoint):
    response = client.get(endpoint)
    assert response.status_code == 401


@pytest.mark.parametrize("endpoint", [
    "/api/producao",
    "/api/processamento",
    "/api/comercializacao",
    "/api/importacao",
    "/api/exportacao"
])
def test_protected_routes_with_access_token(client, tokens, endpoint):
    access = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access}"}
    response = client.get(endpoint, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_refresh_endpoints_requires_refresh_token(client):
    response = client.post("/api/refresh")
    assert response.status_code == 401


def test_refresh_with_valid_refresh_token(client, tokens):
    refresh = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {refresh}"}
    response = client.post("/api/refresh", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    # Opcional: garantir que seja diferente do anterior
    assert data["access_token"] != tokens["access_token"]
