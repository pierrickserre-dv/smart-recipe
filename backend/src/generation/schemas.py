import re
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class RecipeRequest(BaseModel):
    ingredients: List[str] = Field(..., min_length=1, max_length=50)


class RecipeResponse(BaseModel):
    title: str
    prep_time: str
    difficulty: str
    ingredients_used: List[str]
    instructions: List[str]

    @field_validator("ingredients_used")
    @classmethod
    def check_ingredients(cls, v: List[str], info: ValidationInfo):
        if info.context is None:
            return v
        allowed = [
            i.lower().strip() for i in info.context.get("allowed_ingredients", [])
        ]
        staples = {
            "salt",
            "pepper",
            "oil",
            "water",
            "butter",
            "olive oil",
            "garlic",
            "flour",
            "sugar",
        }

        for ing in v:
            ing_lower = ing.lower().strip()
            is_staple = ing_lower in staples
            is_allowed = any(item in ing_lower for item in allowed if item)

            if not is_staple and not is_allowed:
                raise ValueError(f"Unauthorized ingredient used: '{ing}'")
        return v

    @field_validator("instructions")
    @classmethod
    def check_instruction_hallucinations(cls, v: List[str], info: ValidationInfo):
        if info.context is None:
            return v
        allowed_pantry = [
            i.lower().strip() for i in info.context.get("allowed_ingredients", [])
        ]
        staples = {
            "salt",
            "pepper",
            "oil",
            "water",
            "butter",
            "olive oil",
            "garlic",
            "sugar",
            "flour",
        }
        all_authorized = set(allowed_pantry).union(staples)

        forbidden_pool = {
            "cream",
            "milk",
            "cheese",
            "wine",
            "honey",
            "saffron",
            "parsley",
            "lemon",
            "lime",
        }
        full_text = " ".join(v).lower()
        words_in_instructions = set(re.findall(r"\b\w+\b", full_text))

        for word in words_in_instructions:
            if word in forbidden_pool and word not in all_authorized:
                if not any(word in auth for auth in all_authorized):
                    raise ValueError(
                        f"AI hallucinated ingredient in instructions: '{word}'"
                    )
        return v


class SavedRecipe(BaseModel):
    id: str
    title: str
    prep_time: str
    difficulty: str
    ingredients_used: List[str]
    instructions: List[str]
    created_at: Optional[str] = None


class ImageRequest(BaseModel):
    title: str


class ImageResponse(BaseModel):
    image_base64: str
    mime_type: str


class AlternativesRequest(BaseModel):
    selected_ingredients: List[str] = Field(..., min_length=1)
    original_recipe: RecipeResponse


class IngredientAlternative(BaseModel):
    original: str
    alternatives: List[str]


class AlternativesResponse(BaseModel):
    suggestions: List[IngredientAlternative]
    new_recipe: RecipeResponse
