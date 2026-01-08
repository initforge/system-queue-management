from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone as dt_timezone
from uuid import UUID
import logging

from app.models import User, StaffSchedule, Shift
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse, ShiftResponse
)

logger = logging.getLogger(__name__)

class ScheduleService:
    def __init__(self, db: Session):
        self.db = db
    
    # Shift Management
    def get_all_shifts(self) -> List[Shift]:
        """Get all active shifts"""
        return self.db.query(Shift).filter(Shift.is_active == True).all()
    
    def _get_shift_color(self, shift_type: str) -> str:
        """Get color for shift type"""
        colors = {
            "morning": "from-yellow-400 to-orange-500",
            "afternoon": "from-blue-400 to-indigo-500", 
            "night": "from-purple-400 to-pink-500"
        }
        return colors.get(shift_type, "from-gray-400 to-gray-500")
    
    # Schedule Management
    def get_weekly_schedule(
        self, 
        start_date: date, 
        staff_id: Optional[int] = None
    ) -> List[dict]:
        """Get weekly schedule with staff assignments"""
        end_date = start_date + timedelta(days=6)
        
        query = self.db.query(StaffSchedule).options(
            joinedload(StaffSchedule.staff),
            joinedload(StaffSchedule.shift)
        ).filter(
            and_(
                StaffSchedule.scheduled_date >= start_date,
                StaffSchedule.scheduled_date <= end_date
            )
        )
        
        if staff_id:
            query = query.filter(StaffSchedule.staff_id == staff_id)
        
        schedules = query.all()
        
        # Format response
        result = []
        for schedule in schedules:
            result.append(self._format_schedule_response(schedule))
        
        return result
    
    def create_schedule(
        self, 
        schedule_data: ScheduleCreate, 
        manager_id: int
    ) -> dict:
        """Create new schedule entry"""
        # StaffSchedule is already imported at top
        
        # Check for existing schedule on same date/shift
        existing = self.db.query(StaffSchedule).filter(
            and_(
                StaffSchedule.staff_id == schedule_data.staff_id,
                StaffSchedule.scheduled_date == schedule_data.scheduled_date,
                StaffSchedule.shift_id == schedule_data.shift_id
            )
        ).first()
        
        if existing:
            raise ValueError("Staff already scheduled for this shift on this date")
        
        # Create new schedule
        schedule = StaffSchedule(
            staff_id=schedule_data.staff_id,
            manager_id=manager_id,
            shift_id=schedule_data.shift_id,
            scheduled_date=schedule_data.scheduled_date,
            notes=schedule_data.notes,
            status="scheduled"
        )
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        # Reload with relationships to ensure staff and shift are loaded
        schedule = self.db.query(StaffSchedule).options(
            joinedload(StaffSchedule.staff),
            joinedload(StaffSchedule.shift)
        ).filter(StaffSchedule.id == schedule.id).first()
        
        return self._format_schedule_response(schedule)
    
    def update_schedule(
        self, 
        schedule_id: UUID, 
        schedule_data: ScheduleUpdate
    ) -> dict:
        """Update existing schedule"""
        # StaffSchedule is already imported at top
        
        schedule = self.db.query(StaffSchedule).filter(
            StaffSchedule.id == schedule_id
        ).first()
        
        if not schedule:
            raise ValueError("Schedule not found")
        
        # Update fields
        if schedule_data.status:
            schedule.status = schedule_data.status
        if schedule_data.notes is not None:
            schedule.notes = schedule_data.notes
        
        self.db.commit()
        self.db.refresh(schedule)
        
        return self._format_schedule_response(schedule)
    
    def delete_schedule(self, schedule_id: UUID):
        """Delete schedule entry"""
        # StaffSchedule is already imported at top
        
        schedule = self.db.query(StaffSchedule).filter(
            StaffSchedule.id == schedule_id
        ).first()
        
        if not schedule:
            raise ValueError("Schedule not found")
        
        self.db.delete(schedule)
        self.db.commit()
    
    def _format_schedule_response(self, schedule) -> dict:
        """Format schedule for response"""
        staff = schedule.staff
        shift = schedule.shift
        return {
            "id": str(schedule.id),
            "staff_id": schedule.staff_id,
            "staff_name": staff.full_name if staff else "Unknown",
            "staff_username": staff.username if staff else "",
            "staff_email": staff.email if staff else "",
            "staff_avatar": "👤",
            "shift_id": str(schedule.shift_id),
            "shift_name": shift.name if shift else "Unknown",
            "shift_type": shift.shift_type if shift else "other",
            "scheduled_date": schedule.scheduled_date.isoformat(),
            "start_time": shift.start_time.strftime("%H:%M") if shift else "00:00",
            "end_time": shift.end_time.strftime("%H:%M") if shift else "00:00",
            "status": schedule.status,
            "notes": schedule.notes,
            "manager_id": schedule.manager_id,
            "created_at": schedule.created_at
        }