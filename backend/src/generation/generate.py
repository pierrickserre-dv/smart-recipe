import vertexai
from vertexai.generative_models import GenerativeModel

def generate_recipe(ingredients, project_id="your-project-id", location="us-central1"):
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-1.5-flash")

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
    my_ingredients = ["chicken breast", "heavy cream", "spinach", "parmesan cheese", "garlic"]
    
    print("--- Generating your recipe... ---")
    recipe = generate_recipe(my_ingredients)
    print(recipe)