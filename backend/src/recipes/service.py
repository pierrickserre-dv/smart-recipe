import base64

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
        self.image_model_id = "imagen-3.0-generate-002"

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
