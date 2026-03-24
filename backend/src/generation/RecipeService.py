import os
from google import genai
from google.genai import types
from .schemas import RecipeRequest, RecipeResponse

class RecipeAIService:
    def __init__(self):
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "sandbox-pserre")
        
        self.client = genai.Client(
            vertexai=True, 
            project=project_id, 
            location="us-central1"
        )
        self.model_id = "gemini-2.5-flash"

    def generate_recipe(self, data: RecipeRequest) -> RecipeResponse:
        prompt = f"I have these ingredients: {', '.join(data.ingredients)}"
        "Create a creative recipe using ONLY these plus salt, pepper, oil, butter, water, olive oil and/or garlic."
        "Utilize your adaptive thinking to ensure no extra ingredients are added."

        response = self.client.models.generate_content(
            model=self.model_id, 
            contents=prompt, 
            config=types.GenerateContentConfig(
                response_mime_type='application/json', 
                response_schema=RecipeResponse
            )
        )

        recipe_data = response.parsed

        try:
            validated_recipe = RecipeResponse.model_validate(
                recipe_data.model_dump(), 
                context={"allowed_ingredients": data.ingredients}
            )
            return validated_recipe
        except Exception as e:
            print(f"Error: {e}")
            return recipe_data