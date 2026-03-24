from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.auth.dependencies import get_current_user
from src.generation.schemas import RecipeRequest, RecipeResponse
from src.generation.RecipeService import RecipeAIService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

recipe_service = RecipeAIService()

@app.get("/")
def home():
    return {"status": "success", "message": "Backend works!"}

@app.post("/generate", response_model=RecipeResponse)
async def generate_recipe_endpoint(request: RecipeRequest, user=Depends(get_current_user)):
    try:
        recipe_data = recipe_service.generate_recipe(request)
        # Manually trigger validation if the service returns a dict to catch errors here
        if isinstance(recipe_data, dict):
             return RecipeResponse.model_validate(recipe_data, context={"allowed_ingredients": request.ingredients})
        return recipe_data
    except Exception as e:
        # Test requires "error" in the detail string
        raise HTTPException(status_code=500, detail=f"Error: The AI couldn't generate a recipe. {str(e)}")