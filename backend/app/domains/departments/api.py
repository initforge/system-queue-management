from fastapi import APIRouter

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("/")
async def get_departments():
    """Get departments"""
    return {"message": "Departments API - Domain structure"}