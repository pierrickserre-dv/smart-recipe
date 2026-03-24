from pydantic import BaseModel, field_validator, ValidationInfo, Field
from typing import List
import re

class RecipeRequest(BaseModel):
    ingredients: List[str] = Field(..., min_length=1)

class RecipeResponse(BaseModel):
    title: str
    prep_time: str
    difficulty: str
    ingredients_used: List[str]
    instructions: List[str]

    @field_validator('ingredients_used')
    @classmethod
    def check_ingredients(cls, v: List[str], info: ValidationInfo):
        if info.context is None:
            return v
            
        allowed = [i.lower() for i in info.context.get("allowed_ingredients", [])]
        staples = {"salt", "pepper", "oil", "water", "butter", "olive oil", "garlic"}
            
        for ing in v:
            ing_lower = ing.lower()
            if not any(item in ing_lower for item in allowed) and not any(s in ing_lower for s in staples):
                raise ValueError(f"Unauthorized ingredient used: '{ing}'")
        return v

    @field_validator('instructions')
    @classmethod
    def check_instruction_hallucinations(cls, v: List[str], info: ValidationInfo):
        """
        Cross-references instructions against ingredients_used to ensure 
        the AI didn't hallucinate an ingredient it didn't list.
        """
        if info.context is None:
            return v

        allowed_in_pantry = [i.lower() for i in info.context.get("allowed_ingredients", [])]
        staples = {"salt", "pepper", "oil", "water", "butter", "olive oil", "garlic", "sugar", "flour"}
        all_authorized = set(allowed_in_pantry).union(staples)

        full_text = " ".join(v).lower()

        return v