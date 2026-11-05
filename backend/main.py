from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.recipes.controller import router as recipe_controller

app = FastAPI()

app.include_router(recipe_controller, prefix="/recipes", tags=["Recipes"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"status": "success", "message": "Backend works!"}
