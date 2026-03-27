import base64
import json
import os

from google import genai
from google.genai import types

try:
    from .schemas import (
        AlternativesRequest,
        AlternativesResponse,
        IngredientAlternative,
        RecipeRequest,
        RecipeResponse,
    )
except ImportError:
    from schemas import (
        AlternativesRequest,
        AlternativesResponse,
        IngredientAlternative,
        RecipeRequest,
        RecipeResponse,
    )


class RecipeAIService:
    def __init__(self):
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "sandbox-pserre")

        self.client = genai.Client(
            vertexai=True, project=project_id, location="us-central1"
        )

        self.model_id = "gemini-2.5-flash"
        self.image_model_id = "imagen-3.0-generate-002"

    def generate_recipe(self, data: RecipeRequest) -> RecipeResponse:
        prompt = (
            f"I have these ingredients: {', '.join(data.ingredients)}. "
            "Create a creative recipe using ONLY these plus salt, pepper"
            "(not black pepper, just pepper), oil, butter, water, olive oil"
            "and/or garlic."
            "Utilize your adaptive thinking to ensure NO extra ingredients"
            "are added to the list or instructions."
            "If an 'ingredient' prodived does not exist, do NOT use it. "
            "If an ingredient exists but is spelled wrong, you can use it."
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RecipeResponse,
                temperature=0.1,
            ),
        )

        recipe_data = response.parsed

        try:
            validated_recipe = RecipeResponse.model_validate(
                recipe_data.model_dump(),
                context={"allowed_ingredients": data.ingredients},
            )
            return validated_recipe
        except Exception as e:
            print(f"Validation Error: {e}")
            raise e

    def generate_image(self, title: str) -> tuple[str, str]:
        """Generate a preview image for a recipe. Returns (base64_str, mime_type)."""
        prompt = (
            f"A beautiful professional food photograph of '{title}'. "
            "The dish is elegantly plated on a ceramic plate, "
            "soft natural lighting, shallow depth of field, "
            "top-down angle, appetizing and vibrant colors."
        )

        response = self.client.models.generate_images(
            model=self.image_model_id,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                output_mime_type="image/jpeg",
            ),
        )

        image_bytes = response.generated_images[0].image.image_bytes
        return base64.b64encode(image_bytes).decode("utf-8"), "image/jpeg"

    def suggest_alternatives(self, data: AlternativesRequest) -> AlternativesResponse:
        """Suggest alternative ingredients and generate a new recipe."""
        original = data.original_recipe
        selected = data.selected_ingredients

        prompt = (
            f"I have a recipe called '{original.title}' that uses these "
            f"ingredients: {', '.join(original.ingredients_used)}.\n\n"
            f"I want to REPLACE these specific ingredients: "
            f"{', '.join(selected)}.\n\n"
            "For each selected ingredient, suggest 3 alternative ingredients "
            "that could work as substitutes.\n\n"
            "Then create a NEW complete recipe (different title) using "
            "the remaining original ingredients plus one alternative for "
            "each replaced ingredient. The recipe should be coherent and "
            "delicious.\n\n"
            "Return a JSON object with this exact structure:\n"
            "{\n"
            '  "suggestions": [\n'
            '    {"original": "ingredient_name", '
            '"alternatives": ["alt1", "alt2", "alt3"]}\n'
            "  ],\n"
            '  "new_recipe": {\n'
            '    "title": "...",\n'
            '    "prep_time": "...",\n'
            '    "difficulty": "...",\n'
            '    "ingredients_used": ["..."],\n'
            '    "instructions": ["step1", "step2", ...]\n'
            "  }\n"
            "}"
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AlternativesResponse,
                temperature=0.3,
            ),
        )

        parsed = response.parsed
        if isinstance(parsed, AlternativesResponse):
            return parsed

        if isinstance(parsed, dict):
            return AlternativesResponse(**parsed)

        return AlternativesResponse.model_validate(json.loads(str(parsed)))


if __name__ == "__main__":
    rs = RecipeAIService()

    ingredients_list = [
        "chicken breast",
        "heavy cream",
        "spinach",
        "parmesan cheese",
        "garlic",
    ]
    request_data = RecipeRequest(ingredients=ingredients_list)

    print("--- Sending Request to Gemini ---")
    try:
        recipe = rs.generate_recipe(request_data)

        print(f"\nSUCCESS: {recipe.title}")
        print(f"Prep Time: {recipe.prep_time}")
        print(f"Ingredients Used: {', '.join(recipe.ingredients_used)}")
        print("\nInstructions:")
        for i, step in enumerate(recipe.instructions, 1):
            print(f"{i}. {step}")

    except Exception as e:
        print(f"\nFAILED: {e}")
