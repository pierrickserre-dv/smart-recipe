import pytest
from fastapi.testclient import TestClient

from main import app
from src.auth.dependencies import get_current_user

client = TestClient(app)


@pytest.fixture
def mock_user():
    return {"uid": "user_pantry_789", "email": "chef@example.com"}


@pytest.fixture
def override_auth(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


def test_request_min_length_validation(override_auth):
    response = client.post("/recipes/generate", json={"ingredients": []})
    assert response.status_code == 422


def test_request_extreme_input_size(override_auth):
    # With max_length=50 in Schema, 1000 items should return 422, not 500
    huge_payload = {"ingredients": ["ingredient_" + str(i) for i in range(1000)]}
    response = client.post("/recipes/generate", json=huge_payload)
    assert response.status_code == 422


def test_request_non_string_ingredients(override_auth):
    response = client.post("/recipes/generate", json={"ingredients": [123, True]})
    assert response.status_code == 422


def test_request_malformed_json_body(override_auth):
    response = client.post(
        "/recipes/generate",
        content="{'ingredients': ['salt']}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_service_returns_incorrect_types(mocker, override_auth):
    bad_type_data = {
        "title": "Broken AI",
        "prep_time": 10,  # Int instead of Str
        "difficulty": "Easy",
        "ingredients_used": "not a list",
        "instructions": ["Step 1"],
    }
    mocker.patch(
        "src.recipes.controller.recipe_service.generate_recipe",
        return_value=bad_type_data,
    )
    response = client.post("/recipes/generate", json={"ingredients": ["water"]})
    assert response.status_code == 500


def test_service_unhandled_error(mocker, override_auth):
    mocker.patch(
        "src.recipes.controller.recipe_service.generate_recipe",
        side_effect=RuntimeError("API Crash"),
    )
    response = client.post("/recipes/generate", json={"ingredients": ["water"]})
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()


def test_idempotency_simulation(mocker, override_auth):
    mock_recipe = {
        "title": "Repeatable",
        "prep_time": "1m",
        "difficulty": "Easy",
        "ingredients_used": ["salt"],
        "instructions": ["Done"],
    }
    mocker.patch(
        "src.recipes.controller.recipe_service.generate_recipe",
        return_value=mock_recipe,
    )

    res1 = client.post("/recipes/generate", json={"ingredients": ["salt"]})
    res2 = client.post("/recipes/generate", json={"ingredients": ["salt"]})
    assert res1.json() == res2.json()
