from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List

class RecipeRequest(BaseModel):
    ingredients: List[str]

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
        staples = {"sel", "poivre", "huile", "eau", "beurre", "huile d'olive", "ail"}
            
        for ing in v:
            ing_lower = ing.lower()
            if not any(item in ing_lower for item in allowed) and not any(s in ing_lower for s in staples):
                raise ValueError(f"Ingrédient non autorisé détecté : '{ing}'")
        return v