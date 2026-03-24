import firebase_admin
from fastapi import Depends, HTTPException
from firebase_admin import auth
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

firebase_admin.initialize_app()

security = HTTPBearer()

async def get_current_user(res: HTTPAuthorizationCredentials = Depends(security)):
    token = res.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Accès refusé"
        )
