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
        self.model_id = "gemini-2.0-flash" # Note: Ensure your version string is correct

    def generate_recipe(self, data: RecipeRequest) -> RecipeResponse:
        # Combined prompt into a single multi-line string
        prompt = (
            f"I have these ingredients: {', '.join(data.ingredients)}. "
            "Create a creative recipe using ONLY these plus salt, pepper, oil, butter, water, olive oil and/or garlic. "
            "Utilize your adaptive thinking to ensure no extra ingredients are added to the list or instructions."
        )

        response = self.client.models.generate_content(
            model=self.model_id, 
            contents=prompt, 
            config=types.GenerateContentConfig(
                response_mime_type='application/json', 
                response_schema=RecipeResponse
            )
        )

        # response.parsed returns a Pydantic model automatically based on response_schema
        recipe_data = response.parsed

        try:
            # We re-validate with context to trigger our custom 'allowed ingredients' checks
            validated_recipe = RecipeResponse.model_validate(
                recipe_data.model_dump(), 
                context={"allowed_ingredients": data.ingredients}
            )
            return validated_recipe
        except Exception as e:
            # In production, you might want to raise this so main.py catches the 500
            print(f"Validation Error: {e}")
            raise e