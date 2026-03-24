from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.auth.dependencies import get_current_user
from src.generation.schemas import RecipeRequest, RecipeResponse
from src.generation.RecipeService import RecipeService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
) 

@app.get("/bonjour")
def say_bonjour(user = Depends(get_current_user)):
    return {"message": "Private route"}
    
@app.get("/")
def home():
    return {"status": "success", "message": "Backend works!"}

@app.get("/hello")
def say_hello():
    return {"message": "Public route"}


recipe_service = RecipeService()

@app.post("/generate", response_model=RecipeResponse)
async def generate_recipe_endpoint(
    request: RecipeRequest, 
    user=Depends(get_current_user)
):
    try:
        recipe = recipe_service.generate_recipe(request)
        return recipe
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="The AI couldn't generate a recipe.")