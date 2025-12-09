from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta, date
from typing import Optional

from ...core.database import get_db
from ...models import User, DailyLoginLog
from ...core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    get_current_user
)
from sqlalchemy import and_

# Pydantic models
class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    department_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}

router = APIRouter()

@router.get("/test")
def test_endpoint():
    return {"message": "Auth router is working"}



@router.post("/login")
def login(user_credentials: UserLogin, db = Depends(get_db)):
    try:
        # Get user from database by email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check password
        if not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tài khoản đã bị vô hiệu hóa"
            )
        
        # Update last login
        login_time = datetime.utcnow()
        user.last_login = login_time
        db.commit()
        
        # Record first daily login (only once per day)
        today = date.today()
        existing_login = db.query(DailyLoginLog).filter(
            and_(
                DailyLoginLog.user_id == user.id,
                DailyLoginLog.login_date == today
            )
        ).first()
        
        if not existing_login:
            # This is the first login of the day, record it
            daily_login = DailyLoginLog(
                user_id=user.id,
                login_date=today,
                first_login_time=login_time,
                ip_address=None  # Can be added from request if needed
            )
            db.add(daily_login)
            db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            subject=user.email, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "department_id": user.department_id,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

@router.post("/refresh")
def refresh_token(current_user: User = Depends(get_current_user)):
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": current_user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
