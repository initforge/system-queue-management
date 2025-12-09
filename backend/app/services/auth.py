"""
Authentication and User management services
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import bcrypt

from ..core.config import settings
from ..models.user import User
from ..schemas.auth import UserCreate, UserUpdate

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User not found for email: {email}")
            return None
        
        # Check if user is active
        if not user.is_active:
            print(f"User {email} is not active")
            return None
            
        try:
            # Check if password_hash exists
            if not user.password_hash:
                print(f"User {email} has no password hash")
                return None
                
            is_valid = verify_password(password, user.password_hash)
        except Exception as e:
            print(f"Password verification error: {str(e)}")
            print(f"Password hash type: {type(user.password_hash)}")
            print(f"Password hash length: {len(user.password_hash) if user.password_hash else 0}")
            return None
            
        if not is_valid:
            print(f"Invalid password for user: {email}")
            return None
            
        print(f"Authentication successful for user: {email}")
        return user
        
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def create_user(db: Session, user_data: UserCreate) -> User:
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        department_id=user_data.department_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
        
    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password":
            setattr(user, "password_hash", get_password_hash(value))
        else:
            setattr(user, field, value)
            
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()