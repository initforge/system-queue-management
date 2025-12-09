"""
Role-based API Routes
"""
from .staff import router as staff_router
from .manager import router as manager_router

__all__ = ['staff_router', 'manager_router']