"""
Authentication API endpoints (Simplified)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ...core.database import get_db
from ...core.security import get_current_user, require_active_user
from ...models.user import User
from ...schemas.auth import (
    UserLogin, 
    Token, 
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse
)
from ...services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    update_user,
    get_user_by_email
)

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login endpoint"""
    try:
        print(f"Login attempt for email: {user_credentials.email}")
        
        # Try to authenticate user
        user = authenticate_user(db, user_credentials.email, user_credentials.password)
        if not user:
            print(f"Authentication failed for email: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        
        # Prepare response matching Token schema
        response = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 86400,  # 24 hours in seconds
            "user_id": user.id,
            "user_role": user.role
        }
        
        print(f"Login successful for user: {user.email}, role: {user.role}")
        return response
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi trong quá trình đăng nhập. Vui lòng thử lại sau."
        )

@router.post("/register", response_model=UserInDB)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    return create_user(db=db, user_data=user_data)

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@router.put("/me", response_model=UserInDB)
def update_user_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user info"""
    try:
        updated_user = update_user(db, current_user.id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except Exception as e:
        print(f"Update user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update user failed: {str(e)}"
        )

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
