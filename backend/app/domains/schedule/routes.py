from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, time
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse,
    ShiftExchangeCreate, ShiftExchangeResponse,
    CheckinCreate, CheckinResponse,
    ShiftResponse
)
from app.services.schedule_service import ScheduleService
from app.websocket_manager import websocket_manager

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket endpoint for real-time schedule updates
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time schedule updates"""
    try:
        # Get user info for connection
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            await websocket.close(code=4004, reason="User not found")
            return
        
        await websocket_manager.schedule_connect(
            websocket=websocket,
            user_id=user_id,
            user_role=user.role,
            department_id=user.department_id
        )
        
        logger.info(f"WebSocket connected for user {user_id} ({user.role})")
        
        # Keep connection alive and handle messages
        while True:
            try:
                data = await websocket.receive_text()
                # Handle incoming messages if needed
                logger.info(f"Received WebSocket message from user {user_id}: {data}")
                
                # Echo back for now
                await websocket_manager.send_schedule_message(websocket, {
                    "type": "echo",
                    "message": f"Received: {data}",
                    "timestamp": datetime.now().isoformat()
                })
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user_id}")
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        websocket_manager.schedule_disconnect(websocket)
logger = logging.getLogger(__name__)

@router.get("/shifts", response_model=List[ShiftResponse])
async def get_shifts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available shifts"""
    try:
        service = ScheduleService(db)
        shifts = service.get_all_shifts()
        return shifts
    except Exception as e:
        logger.error(f"Error getting shifts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving shifts"
        )

@router.get("/schedule/week", response_model=List[ScheduleResponse])
async def get_weekly_schedule(
    start_date: date,
    staff_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weekly schedule for staff or manager"""
    try:
        service = ScheduleService(db)
        
        # If staff_id not provided, get current user's schedule
        if not staff_id and current_user.role == 'staff':
            staff_id = current_user.id
        
        # Managers can see all schedules, staff only their own
        if current_user.role == 'staff' and staff_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff can only view their own schedule"
            )
        
        schedules = service.get_weekly_schedule(start_date, staff_id)
        return schedules
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weekly schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving schedule"
        )

@router.post("/schedule", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new schedule entry (Manager only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can create schedules"
        )
    
    try:
        service = ScheduleService(db)
        schedule = service.create_schedule(schedule_data, current_user.id)
        
        # Send real-time notification
        await websocket_manager.notify_schedule_updated(
            schedule_data=schedule.dict(),
            department_id=current_user.department_id
        )
        
        return schedule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating schedule"
        )

@router.put("/schedule/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update schedule entry (Manager only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can update schedules"
        )
    
    try:
        service = ScheduleService(db)
        schedule = service.update_schedule(schedule_id, schedule_data)
        return schedule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating schedule"
        )

@router.delete("/schedule/{schedule_id}")
async def delete_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete schedule entry (Manager only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can delete schedules"
        )
    
    try:
        service = ScheduleService(db)
        service.delete_schedule(schedule_id)
        return {"message": "Schedule deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting schedule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting schedule"
        )

# Leave Request Endpoints
@router.get("/leave-requests", response_model=List[LeaveRequestResponse])
async def get_leave_requests(
    status_filter: Optional[str] = None,
    staff_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get leave requests - staff see their own, managers see all"""
    try:
        service = ScheduleService(db)
        
        if current_user.role == 'staff':
            # Staff can only see their own requests
            requests = service.get_leave_requests(staff_id=current_user.id, status_filter=status_filter)
        else:
            # Managers can see all or filtered requests
            requests = service.get_leave_requests(staff_id=staff_id, status_filter=status_filter)
        
        return requests
    except Exception as e:
        logger.error(f"Error getting leave requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving leave requests"
        )

@router.post("/leave-requests", response_model=LeaveRequestResponse)
async def create_leave_request(
    request_data: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create leave request (Staff only)"""
    try:
        service = ScheduleService(db)
        request = service.create_leave_request(request_data, current_user.id)
        
        # Send real-time notification to managers
        await websocket_manager.notify_leave_request_submitted(
            leave_request_data=request.dict(),
            department_id=current_user.department_id
        )
        
        return request
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating leave request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating leave request"
        )

@router.put("/leave-requests/{request_id}", response_model=LeaveRequestResponse)
async def update_leave_request(
    request_id: UUID,
    request_data: LeaveRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update leave request status (Manager only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can approve/reject leave requests"
        )
    
    try:
        service = ScheduleService(db)
        request = service.update_leave_request(request_id, request_data, current_user.id)
        
        # Get staff ID from the updated request to notify them
        if hasattr(request, 'staff_id'):
            await websocket_manager.notify_leave_request_reviewed(
                leave_request_data=request.dict(),
                staff_id=request.staff_id
            )
        
        return request
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating leave request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating leave request"
        )

# Check-in Endpoints
@router.get("/checkins", response_model=List[CheckinResponse])
async def get_checkins(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get check-in requests (Manager only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can view check-in requests"
        )
    
    try:
        service = ScheduleService(db)
        checkins = service.get_checkins(status_filter=status_filter)
        return checkins
    except Exception as e:
        logger.error(f"Error getting check-ins: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving check-ins"
        )

@router.post("/checkins", response_model=CheckinResponse)
async def create_checkin(
    checkin_data: CheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create check-in request (Staff only)"""
    try:
        service = ScheduleService(db)
        checkin = service.create_checkin(checkin_data, current_user.id)
        return checkin
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating check-in: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating check-in"
        )

@router.put("/checkins/{checkin_id}/approve")
async def approve_checkin(
    checkin_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve check-in request (Manager only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can approve check-ins"
        )
    
    try:
        service = ScheduleService(db)
        checkin = service.approve_checkin(checkin_id, current_user.id)
        return checkin
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error approving check-in: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error approving check-in"
        )

@router.put("/checkins/{checkin_id}/reject")
async def reject_checkin(
    checkin_id: UUID,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject check-in request (Manager only)"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can reject check-ins"
        )
    
    try:
        service = ScheduleService(db)
        checkin = service.reject_checkin(checkin_id, reason, current_user.id)
        return checkin
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error rejecting check-in: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error rejecting check-in"
        )