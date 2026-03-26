import pytest
from fastapi.testclient import TestClient

from main import app
from src.auth.dependencies import get_current_user
from src.generation.schemas import RecipeResponse

client = TestClient(app)


@pytest.fixture
def mock_user():
    return {"uid": "user_pantry_789", "email": "chef@example.com"}


@pytest.fixture
def override_auth(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


# --- 1. AUTHENTICATION & SECURITY DEPTH ---


def test_auth_no_header():
    response = client.post("/generate", json={"ingredients": ["tomato"]})
    assert response.status_code == 401


def test_auth_invalid_scheme():
    headers = {"Authorization": "Basic dXNlcjpwYXNz"}
    response = client.post(
        "/generate", json={"ingredients": ["tomato"]}, headers=headers
    )
    assert response.status_code == 401


def test_auth_empty_token():
    headers = {"Authorization": "Bearer "}
    response = client.post(
        "/generate", json={"ingredients": ["tomato"]}, headers=headers
    )
    assert response.status_code == 401


# --- 2. INPUT VALIDATION & EDGE CASES ---


def test_request_min_length_validation(override_auth):
    response = client.post("/generate", json={"ingredients": []})
    assert response.status_code == 422


def test_request_extreme_input_size(override_auth):
    # With max_length=50 in Schema, 1000 items should return 422, not 500
    huge_payload = {"ingredients": ["ingredient_" + str(i) for i in range(1000)]}
    response = client.post("/generate", json=huge_payload)
    assert response.status_code == 422


def test_request_non_string_ingredients(override_auth):
    response = client.post("/generate", json={"ingredients": [123, True]})
    assert response.status_code == 422


def test_request_malformed_json_body(override_auth):
    response = client.post(
        "/generate",
        content="{'ingredients': ['salt']}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


# --- 3. PYDANTIC VALIDATOR ROBUSTNESS ---


@pytest.mark.parametrize("ingredient", ["SALT", "pEpPeR", "  Garlic  ", "olive oil"])
def test_validator_handles_staple_casing_and_whitespace(ingredient):
    data = {
        "title": "Staple Test",
        "prep_time": "1m",
        "difficulty": "Easy",
        "ingredients_used": [ingredient],
        "instructions": ["Use it."],
    }
    validated = RecipeResponse.model_validate(data, context={"allowed_ingredients": []})
    assert ingredient in validated.ingredients_used


def test_validator_complex_substring_protection():
    data = {
        "title": "Oil Test",
        "prep_time": "1m",
        "difficulty": "Easy",
        "ingredients_used": ["chili oil"],
        "instructions": ["Add oil"],
    }
    # Should fail because 'chili' isn't authorized, even if 'oil' is a staple
    with pytest.raises(ValueError, match="Unauthorized"):
        RecipeResponse.model_validate(data, context={"allowed_ingredients": ["salt"]})


# --- 4. AI SERVICE FAILURE MODES (MOCKED) ---


def test_service_returns_incorrect_types(mocker, override_auth):
    bad_type_data = {
        "title": "Broken AI",
        "prep_time": 10,  # Int instead of Str
        "difficulty": "Easy",
        "ingredients_used": "not a list",
        "instructions": ["Step 1"],
    }
    mocker.patch("main.recipe_service.generate_recipe", return_value=bad_type_data)
    response = client.post("/generate", json={"ingredients": ["water"]})
    assert response.status_code == 500


def test_service_unhandled_error(mocker, override_auth):
    mocker.patch(
        "main.recipe_service.generate_recipe", side_effect=RuntimeError("API Crash")
    )
    response = client.post("/generate", json={"ingredients": ["water"]})
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()


# --- 5. LOGIC & DATA INTEGRITY ---


def test_idempotency_simulation(mocker, override_auth):
    mock_recipe = {
        "title": "Repeatable",
        "prep_time": "1m",
        "difficulty": "Easy",
        "ingredients_used": ["salt"],
        "instructions": ["Done"],
    }
    mocker.patch("main.recipe_service.generate_recipe", return_value=mock_recipe)

    res1 = client.post("/generate", json={"ingredients": ["salt"]})
    res2 = client.post("/generate", json={"ingredients": ["salt"]})
    assert res1.json() == res2.json()


def test_instruction_scrubber_full_logic_check():
    raw_ai_output = {
        "title": "Ghost Soup",
        "prep_time": "5m",
        "difficulty": "Easy",
        "ingredients_used": ["water", "salt"],
        "instructions": ["Boil water", "Secretly add heavy cream", "Serve"],
    }
    with pytest.raises(ValueError, match="hallucinated"):
        RecipeResponse.model_validate(
            raw_ai_output, context={"allowed_ingredients": ["water"]}
        )


# --- 6. CORS & HEADERS ---


def test_cors_preflight():
    response = client.options(
        "/generate",
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4200"


# --- 7. RECOVERY TEST ---


def test_app_recovers_after_fail(mocker, override_auth):
    mocker.patch(
        "main.recipe_service.generate_recipe",
        side_effect=[
            Exception("Transient Fail"),
            {
                "title": "Success",
                "prep_time": "1m",
                "difficulty": "Easy",
                "ingredients_used": ["salt"],
                "instructions": ["Step"],
            },
        ],
    )

    first_res = client.post("/generate", json={"ingredients": ["salt"]})
    assert first_res.status_code == 500

    second_res = client.post("/generate", json={"ingredients": ["salt"]})
    assert second_res.status_code == 200
    assert second_res.json()["title"] == "Success"
