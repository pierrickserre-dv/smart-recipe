import re
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

FORBIDDEN_POOL = {
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

    @field_validator("instructions")
    @classmethod
    def check_instruction_hallucinations(cls, v: List[str], info: ValidationInfo):
        if info.context is None:
            return v
        allowed_pantry = [
            i.lower().strip() for i in info.context.get("allowed_ingredients", [])
        ]
        all_authorized = set(allowed_pantry).union(STAPLES)

        full_text = " ".join(v).lower()
        words_in_instructions = set(re.findall(r"\b\w+\b", full_text))

        for word in words_in_instructions:
            if word in FORBIDDEN_POOL and word not in all_authorized:
                if not any(word in auth for auth in all_authorized):
                    raise ValueError(
                        f"AI hallucinated ingredient in instructions: '{word}'"
                    )
        return v
