import os
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv()

def generate_recipe(ingredients, project_id, location):
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-2.5-pro")

    prompt = f"""
    I have the following ingredients: {', '.join(ingredients)}.
    Please generate a creative recipe including:
    1. A catchy Title.
    2. Prep and Cook time.
    3. A full list of ingredients (you can assume I have salt, pepper, and oil).
    4. Step-by-step instructions.
    """

    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    ingredients = ["chicken breast", "heavy cream", "spinach", "parmesan cheese", "garlic"]

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    print("--- Generating your recipe... ---")
    recipe = generate_recipe(ingredients, project_id, location)
    print(recipe)