
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class UserRoleUpdate(BaseModel):
    role: Literal["user", "admin"]
