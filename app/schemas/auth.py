
from pydantic import BaseModel, EmailStr, Field
from typing import Literal


# 1. Registration Schema
class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# 2. Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 3. Token Response Schema
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


# 4. Token Refresh Schema
class TokenRefresh(BaseModel):
    refresh_token: str
