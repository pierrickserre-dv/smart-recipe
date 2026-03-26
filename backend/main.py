from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.auth.dependencies import get_current_user
from src.auth.schemas import User
from src.generation.persistence import FirestoreService
from src.generation.RecipeService import RecipeAIService
from src.generation.schemas import RecipeRequest, RecipeResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

recipe_service = RecipeAIService()
firestore = FirestoreService()


@app.get("/")
def home():
    return {"status": "success", "message": "Backend works!"}


@app.post("/generate", response_model=RecipeResponse)
async def generate_recipe_endpoint(
    request: RecipeRequest, user=Depends(get_current_user)
):
    try:
        recipe_data = recipe_service.generate_recipe(request)
        if isinstance(recipe_data, dict):
            return RecipeResponse.model_validate(
                recipe_data, context={"allowed_ingredients": request.ingredients}
            )
        return recipe_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: The AI couldn't generate a recipe. {str(e)}",
        )


@app.post("/save")
async def save_recipe(request: RecipeResponse, user: User = Depends(get_current_user)):
    try:
        recipe_id = await firestore.save_recipe_for_user(user.uid, request)
        return {
            "status": "success",
            "message": "Recipe saved successfully",
            "id": recipe_id,
        }
    except Exception as e:
        print(f"DEBUG: Firestore Error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while saving the recipe to the database.",
        )
