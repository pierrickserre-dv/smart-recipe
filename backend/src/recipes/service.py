from google import genai
from google.genai import types

from src.config import settings

try:
    from .schemas import RecipeRequest, RecipeResponse
except ImportError:
    from schemas import RecipeRequest, RecipeResponse


class RecipeAIService:
    def __init__(self):
        self.model_id = "gemini-2.5-flash"

        self.client = genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
        )

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

