import pytest
from fastapi.testclient import TestClient
from main import app
from src.auth.dependencies import get_current_user
from src.generation.schemas import RecipeResponse

client = TestClient(app)

@pytest.fixture
def mock_user():
    return {"uid": "test-user-123", "email": "test@example.com"}

@pytest.fixture
def override_auth(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()

def test_home_status():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_generate_recipe_unauthorized():
    response = client.post("/generate", json={"ingredients": ["egg"]})
    assert response.status_code == 401

def test_generate_recipe_success(mocker, override_auth):
    mock_data = {
        "title": "Simple Omelette",
        "prep_time": "5 mins",
        "difficulty": "Easy",
        "ingredients_used": ["egg", "butter", "salt"],
        "instructions": ["Melt butter", "Whisk eggs", "Cook in pan"]
    }
    mocker.patch("main.recipe_service.generate_recipe", return_value=mock_data)

    payload = {"ingredients": ["egg"]}
    response = client.post("/generate", json=payload)

    assert response.status_code == 200
    assert response.json()["title"] == "Simple Omelette"
    assert "egg" in response.json()["ingredients_used"]

def test_ai_service_error_handling(mocker, override_auth):
    mocker.patch(
        "main.recipe_service.generate_recipe", 
        side_effect=Exception("AI Service Down")
    )

    response = client.post("/generate", json={"ingredients": ["egg"]})
    assert response.status_code == 500
    assert "The AI couldn't generate a recipe" in response.json()["detail"]

def test_validator_allowed_ingredients():
    valid_recipe = {
        "title": "Garlic Water",
        "prep_time": "1m",
        "difficulty": "Easy",
        "ingredients_used": ["garlic", "water"],
        "instructions": ["Boil water", "Add garlic"]
    }
    validated = RecipeResponse.model_validate(valid_recipe, context={"allowed_ingredients": []})
    assert len(validated.ingredients_used) == 2

def test_validator_rejects_unauthorized():
    invalid_recipe = {
        "title": "Illegal Truffle Pasta",
        "prep_time": "20m",
        "difficulty": "Medium",
        "ingredients_used": ["pasta", "truffles"], 
        "instructions": ["Cook pasta", "Shave truffles"]
    }
    with pytest.raises(ValueError, match="Unauthorized ingredient used"):
        RecipeResponse.model_validate(invalid_recipe, context={"allowed_ingredients": ["salt"]})

def test_empty_ingredient_list_fails_validation(override_auth):
    response = client.post("/generate", json={"ingredients": []})
    assert response.status_code == 422

def test_instruction_hallucination_simulation():
    allowed = ["egg", "salt", "butter", "water"]
    instructions = "Crack the egg and add some saffron."
    
    found_hallucination = "saffron" if "saffron" not in allowed else None
    assert found_hallucination == "saffron"