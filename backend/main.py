from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.recipes.controller import router as recipe_controller
from src.recipes.schemas import ImageRequest, ImageResponse
from src.recipes.service import RecipeAIService
from src.auth.dependencies import get_current_user

app = FastAPI()

app.include_router(recipe_controller, prefix="/recipes", tags=["Recipes"])

recipe_service = RecipeAIService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "success", "message": "Backend works!"}


@app.post("/generate-image", response_model=ImageResponse)
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
