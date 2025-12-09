# User Pydantic Schemas
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    MANAGER = "manager"
    ADMIN = "admin"

# Base User Schema
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole = UserRole.CUSTOMER
    department_id: Optional[int] = None
    is_active: bool = True

# User Creation Schema
class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

# User Update Schema
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

# User Response Schema
class UserResponse(UserBase):
    id: int
    created_at: datetime
    department_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

# User Profile Schema  
class UserProfile(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    department_id: Optional[int]
    department_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True