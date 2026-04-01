from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_auth_no_header():
    response = client.post("/recipes/generate", json={"ingredients": ["tomato"]})
    assert response.status_code == 401


def test_auth_invalid_scheme():
    headers = {"Authorization": "Basic dXNlcjpwYXNz"}
    response = client.post(
        "/recipes/generate", json={"ingredients": ["tomato"]}, headers=headers
    )
    assert response.status_code == 401


def test_auth_empty_token():
    headers = {"Authorization": "Bearer "}
    response = client.post(
        "/recipes/generate", json={"ingredients": ["tomato"]}, headers=headers
    )
    assert response.status_code == 401


def test_cors_preflight():
    response = client.options(
        "/recipes/generate",
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4200"
