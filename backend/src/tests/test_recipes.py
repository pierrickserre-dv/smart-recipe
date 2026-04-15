import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

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


def test_generate_image_success(mocker, override_auth):
    mocker.patch(
        "src.recipes.controller.recipe_service.generate_image",
        return_value=("aW1hZ2VfZGF0YQ==", "image/jpeg"),
    )
    response = client.post("/recipes/generate-image", json={"title": "Pasta Carbonara"})
    assert response.status_code == 200
    data = response.json()
    assert data["image_base64"] == "aW1hZ2VfZGF0YQ=="
    assert data["mime_type"] == "image/jpeg"


def test_generate_image_missing_title(override_auth):
    response = client.post("/recipes/generate-image", json={})
    assert response.status_code == 422


def test_generate_image_service_error(mocker, override_auth):
    mocker.patch(
        "src.recipes.controller.recipe_service.generate_image",
        side_effect=RuntimeError("Imagen API down"),
    )
    response = client.post("/recipes/generate-image", json={"title": "Pasta"})
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()


def test_get_account_equipment(mocker, override_auth):
    mocker.patch(
        "src.recipes.controller.firestore.get_user_equipment",
        new=AsyncMock(return_value=["oven", "air fryer"]),
    )
    response = client.get("/recipes/account/equipment")
    assert response.status_code == 200
    assert response.json() == {"equipment": ["oven", "air fryer"]}


def test_update_account_equipment(mocker, override_auth):
    mocker.patch(
        "src.recipes.controller.firestore.save_user_equipment",
        new=AsyncMock(return_value=["oven", "pan"]),
    )
    response = client.put(
        "/recipes/account/equipment", json={"equipment": ["oven", "pan", "pan"]}
    )
    assert response.status_code == 200
    assert response.json() == {"equipment": ["oven", "pan"]}
