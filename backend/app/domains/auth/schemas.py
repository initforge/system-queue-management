from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .models import UserRole

# Request schemas
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    role: UserRole
    department_id: Optional[int] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# Response schemas
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str]
    full_name: str
    role: str
    department_id: Optional[int]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str]
    full_name: str
    role: str
    department_id: Optional[int]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile