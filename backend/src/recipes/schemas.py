from typing import List

from pydantic import BaseModel, Field, ValidationInfo, field_validator

STAPLES = {
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

        for ing in v:
            ing_lower = ing.lower().strip()
            is_staple = ing_lower in STAPLES
            is_allowed = any(item in ing_lower for item in allowed if item)

            if not is_staple and not is_allowed:
                raise ValueError(f"Unauthorized ingredient used: '{ing}'")
        return v
