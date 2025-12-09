# Authentication Pydantic Schemas
from pydantic import BaseModel, EmailStr
from typing import Optional

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_id: int
    user_role: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

# User Schemas
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "user"
    department_id: Optional[int] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    department_id: Optional[int] = None

class UserInDB(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool = True
    department_id: Optional[int] = None

    class Config:
        from_attributes = True

# Response Models
class UserResponse(UserInDB):
    pass
    password: str
    remember_me: bool = False

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[Token] = None
    user: Optional[dict] = None

# Registration Schemas
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    confirm_password: str
    
    def validate_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Passwords do not match')
        return self

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None

# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    confirm_password: str

# Change Password Schema
class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str