"""
API Router v1 - Main router for version 1 of the API
"""
from fastapi import APIRouter
from . import auth_router, departments_router
from .tickets import router as tickets_router
from .staff import router as staff_router
from .services import router as services_router

# Create main API v1 router
api_router = APIRouter()

# Include auth router
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Include essential routers
api_router.include_router(departments_router, prefix="/departments", tags=["Departments"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(staff_router, prefix="/staff", tags=["Staff"])
api_router.include_router(services_router, prefix="/services", tags=["Services"])
