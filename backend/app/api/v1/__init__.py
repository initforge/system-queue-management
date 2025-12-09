"""
Router package for Queue Management System API endpoints
"""

from .auth import router as auth_router
from .departments import router as departments_router

__all__ = [
    "auth_router",
    "departments_router"
]