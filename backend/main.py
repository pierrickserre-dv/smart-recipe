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

@app.get("/bonjour")
def say_bonjour(user = Depends(get_current_user)):
    return {"message": "Route privée"}
    
@app.get("/")
def home():
    return {"status": "success", "message": "Le backend fonctionne!"}

@app.get("/hello")
def say_hello():
    return {"message": "Route publique"}


recipe_service = RecipeAIService()

@app.post("/generate", response_model=RecipeResponse)
async def generate_recipe_endpoint(
    request: RecipeRequest, 
    user=Depends(get_current_user)
):
    try:
        recipe = recipe_service.generate_recipe(request)
        return recipe
    except Exception as e:
        print(f"Erreur génération : {str(e)}")
        raise HTTPException(status_code=500, detail="L'IA n'a pas pu générer la recette.")