from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UserCreate, UserResponse, UserLogin, TokenResponse, PasswordChange, UserProfile
from .services import AuthService
from ...shared.core.database import get_db
from ...shared.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    user = await auth_service.create_user(user_data)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    auth_service = AuthService(db)
    access_token, user = await auth_service.login(login_data)
    
    user_profile = UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role,
        department_id=user.department_id
    )
    
    return TokenResponse(
        access_token=access_token,
        user=user_profile
    )

@router.get("/me", response_model=UserProfile)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user information"""
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        full_name=current_user.full_name,
        role=current_user.role,
        department_id=current_user.department_id
    )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    auth_service = AuthService(db)
    await auth_service.change_password(current_user.id, password_data)
    return {"message": "Password changed successfully"}

@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Logged out successfully"}