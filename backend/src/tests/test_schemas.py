import pytest
from fastapi.testclient import TestClient

from main import app
from src.auth.dependencies import get_current_user
from src.recipes.schemas import RecipeResponse

client = TestClient(app)


@pytest.fixture
def mock_user():
    return {"uid": "user_pantry_789", "email": "chef@example.com"}


@pytest.fixture
def override_auth(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


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
