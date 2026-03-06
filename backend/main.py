from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.auth.dependencies import get_current_user

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

