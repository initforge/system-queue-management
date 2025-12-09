#!/usr/bin/env python3
"""
Script để tạo user admin mới với password hash đúng
"""
import sys
import os
sys.path.append('/app')

from passlib.context import CryptContext
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.core.config import settings

# Tạo password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def create_admin_user():
    # Tạo kết nối database
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # Xóa user admin cũ nếu có
        old_admin = db.query(User).filter(User.email == "admin@test.com").first()
        if old_admin:
            db.delete(old_admin)
        
        # Tạo password hash
        password_hash = pwd_context.hash("admin123")
        print(f"Password hash: {password_hash}")
        
        # Tạo user admin mới
        admin_user = User(
            username="admin",
            password_hash=password_hash,
            email="admin@test.com",
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Tạo admin user thành công:")
        print(f"Email: admin@test.com")
        print(f"Password: admin123")
        print(f"User ID: {admin_user.id}")
        
    except Exception as e:
        print(f"Lỗi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()