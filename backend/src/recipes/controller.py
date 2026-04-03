from fastapi import APIRouter, Depends, HTTPException

from src.auth.dependencies import get_current_user
from src.auth.schemas import User
from src.recipes.persistence import FirestoreService
from src.recipes.schemas import ImageRequest, ImageResponse, RecipeRequest, RecipeResponse
from src.recipes.service import RecipeAIService

router = APIRouter()

recipe_service = RecipeAIService()
firestore = FirestoreService()


@router.post("/generate", response_model=RecipeResponse)
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


@router.post("/save")
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


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: str, user: User = Depends(get_current_user)):
    try:
        await firestore.delete_recipe_for_user(user.uid, recipe_id)
        return {
            "status": "success",
            "message": f"Recipe {recipe_id} deleted successfully",
        }
    except Exception as e:
        print(f"DEBUG: Firestore Error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while deleting the recipe from the database.",
        )


@router.get("")
async def get_recipes(user: User = Depends(get_current_user)):
    try:
        recipes = await firestore.get_recipes(user.uid)
        return recipes
    except Exception as e:
        print(f"DEBUG: Firestore Error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occured while getting the recipes from the database",
        )


@router.post("/generate-image", response_model=ImageResponse)
def generate_image(request: ImageRequest, user=Depends(get_current_user)):
    try:
        image_base64, mime_type = recipe_service.generate_image(request.title)
        return ImageResponse(image_base64=image_base64, mime_type=mime_type)
    except Exception as e:
        print(f"DEBUG: Image generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the recipe image.",
        )
