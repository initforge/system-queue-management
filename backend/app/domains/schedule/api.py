from fastapi import APIRouter

router = APIRouter(prefix="/schedule", tags=["schedule"])

@router.get("/")
async def get_schedule():
    """Get schedule"""
    return {"message": "Schedule API - Domain structure"}