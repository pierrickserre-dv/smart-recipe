import firebase_admin
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from .schemas import User

if not firebase_admin._apps:
    firebase_admin.initialize_app()

security = HTTPBearer()


async def get_current_user(
    res: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    token = res.credentials
    try:
        decoded_token = auth.verify_id_token(token)

        return User(
            uid=decoded_token.get("uid"),
            email=decoded_token.get("email"),
            name=decoded_token.get("name"),
        )

    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
