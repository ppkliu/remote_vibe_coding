from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
import uuid

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr | None = None

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    last_login: datetime | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
