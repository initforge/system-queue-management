from fastapi import APIRouter

router = APIRouter(prefix="/queue", tags=["queue"])

@router.get("/")
async def get_queue():
    """Get queue status"""
    return {"message": "Queue API - Domain structure"}