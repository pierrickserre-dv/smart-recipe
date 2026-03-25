import os
from google import genai
from google.genai import types
try:
    from .schemas import RecipeRequest, RecipeResponse
except ImportError:
    from schemas import RecipeRequest, RecipeResponse

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
        prompt = (
            f"I have these ingredients: {', '.join(data.ingredients)}. "
            "Create a creative recipe using ONLY these plus salt, pepper (not black pepper, just pepper), oil, butter, water, olive oil and/or garlic. "
            "Utilize your adaptive thinking to ensure NO extra ingredients are added to the list or instructions."
        )

        response = self.client.models.generate_content(
            model=self.model_id, 
            contents=prompt, 
            config=types.GenerateContentConfig(
                response_mime_type='application/json', 
                response_schema=RecipeResponse,
                temperature=0.1
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
            print(f"Validation Error: {e}")
            raise e

if __name__ == "__main__":
    rs = RecipeAIService()

    ingredients_list = ["chicken breast", "heavy cream", "spinach", "parmesan cheese", "garlic"]
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