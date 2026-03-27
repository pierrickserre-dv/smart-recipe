from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    uid: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
