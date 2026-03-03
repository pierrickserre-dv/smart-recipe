import json
import firebase_admin
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import secretmanager
from firebase_admin import credentials, auth
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def get_firebase_app():
    try:
        return firebase_admin.get_app()
    except ValueError:
        client = secretmanager.SecretManagerServiceClient()
        project_id = "sandbox-pserre"
        name = f"projects/{project_id}/secrets/FIREBASE_ADMIN_SDK/versions/latest"
        response = client.access_secret_version(request={"name": name})
        secret_dict = json.loads(response.payload.data.decode("UTF-8"))
        cred = credentials.Certificate(secret_dict)
        return firebase_admin.initialize_app(cred)

get_firebase_app()

security = HTTPBearer()

async def get_current_user(res: HTTPAuthorizationCredentials = Depends(security)):
    token = res.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token

    except Exception:
        raise HTTPException(
            status_code=401,
            details="Accès refusé"
        )

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

