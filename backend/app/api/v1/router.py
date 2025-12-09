from fastapi import APIRouter
from ...domains.auth.api import router as auth_router
from ...domains.queue.api import router as queue_router  
from ...domains.schedule.api import router as schedule_router
from ...domains.departments.api import router as departments_router

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include domain routers
api_router.include_router(auth_router)
api_router.include_router(queue_router)
api_router.include_router(schedule_router)
api_router.include_router(departments_router)

# Role-based routers (aggregated endpoints) - implement later
# from .roles.staff import router as staff_router
# from .roles.manager import router as manager_router

# api_router.include_router(staff_router, prefix="/staff", tags=["staff"])
# api_router.include_router(manager_router, prefix="/manager", tags=["manager"])