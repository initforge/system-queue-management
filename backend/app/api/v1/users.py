from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from ...core.database import get_db
from ...models import User, Department, UserRole
from ...core.security import get_current_user, get_password_hash

router = APIRouter()

# Pydantic models
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str]
    full_name: str
    role: UserRole
    department_id: Optional[int]
    department_name: Optional[str]
    counter_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    model_config = {"from_attributes": True}

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    phone: Optional[str] = None
    full_name: str
    role: UserRole
    department_id: Optional[int] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.get("/", response_model=List[UserResponse])
async def get_users(
    department_id: Optional[int] = None,
    role: Optional[UserRole] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    query = select(User, Department).outerjoin(Department, User.department_id == Department.id)
    
    if department_id:
        query = query.where(User.department_id == department_id)
    
    if role:
        query = query.where(User.role == role)
    
    if not include_inactive:
        query = query.where(User.is_active == True)
    
    result = await db.execute(query.order_by(User.full_name))
    users = result.all()
    
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            role=user.role,
            department_id=user.department_id,
            department_name=department.name if department else None,
            counter_id=user.counter_id,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        for user, department in users
    ]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    result = await db.execute(
        select(User, Department)
        .outerjoin(Department, User.department_id == Department.id)
        .where(User.id == user_id)
    )
    user_data = result.first()
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user, department = user_data
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role,
        department_id=user.department_id,
        department_name=department.name if department else None,
        counter_id=user.counter_id,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login
    )

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Check if username already exists
    existing_user = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email already exists
    existing_email = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_email.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        role=user_data.role,
        department_id=user_data.department_id
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Get department name for response
    department = None
    if new_user.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == new_user.department_id)
        )
        department = dept_result.scalar_one_or_none()
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        phone=new_user.phone,
        full_name=new_user.full_name,
        role=new_user.role,
        department_id=new_user.department_id,
        department_name=department.name if department else None,
        counter_id=new_user.counter_id,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        last_login=new_user.last_login
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.email is not None:
        # Check if email already exists
        existing_email = await db.execute(
            select(User).where(User.email == user_data.email, User.id != user_id)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        user.email = user_data.email
    
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.department_id is not None:
        user.department_id = user_data.department_id
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    await db.commit()
    await db.refresh(user)
    
    # Get department name for response
    department = None
    if user.department_id:
        dept_result = await db.execute(
            select(Department).where(Department.id == user.department_id)
        )
        department = dept_result.scalar_one_or_none()
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        phone=user.phone,
        full_name=user.full_name,
        role=user.role,
        department_id=user.department_id,
        department_name=department.name if department else None,
        counter_id=user.counter_id,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login=user.last_login
    )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from ...core.security import verify_password
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()
    
    return {"message": "Password changed successfully"}

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete (deactivate)
    user.is_active = False
    await db.commit()
    
    return {"message": "User deactivated successfully"}
