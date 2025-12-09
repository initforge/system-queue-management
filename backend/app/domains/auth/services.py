from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from passlib.context import CryptContext

from .models import User, UserRole
from .schemas import UserCreate, UserUpdate, UserLogin, PasswordChange
from ...shared.core.security import create_access_token, verify_password, get_password_hash

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            # Check if username or email already exists
            existing_user = await self.db.execute(
                select(User).where(
                    (User.username == user_data.username) | 
                    (User.email == user_data.email)
                )
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already registered"
                )

            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            db_user = User(
                username=user_data.username,
                password_hash=hashed_password,
                email=user_data.email,
                phone=user_data.phone,
                full_name=user_data.full_name,
                role=user_data.role,
                department_id=user_data.department_id
            )
            
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
            
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )

    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with username and password"""
        result = await self.db.execute(
            select(User).where(
                User.username == login_data.username,
                User.is_active == True
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
            
        if not verify_password(login_data.password, user.password_hash):
            return None
            
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User).where(User.username == username, User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def change_password(self, user_id: int, password_data: PasswordChange) -> bool:
        """Change user password"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify old password
        if not verify_password(password_data.old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid old password"
            )
        
        # Update password
        user.password_hash = get_password_hash(password_data.new_password)
        await self.db.commit()
        return True

    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        await self.db.commit()
        return True

    async def login(self, login_data: UserLogin) -> tuple[str, User]:
        """Login user and return access token"""
        user = await self.authenticate_user(login_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        await self.db.commit()
        
        # Create access token
        access_token = create_access_token(subject=user.id)
        return access_token, user