from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone as dt_timezone
from uuid import UUID
import logging

from app.models import User, DailyLoginLog, LeaveRequest, StaffSchedule, Shift, StaffCheckin
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse,
    CheckinCreate, CheckinResponse, ShiftResponse
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
            "created_at": schedule.created_at,
            "updated_at": schedule.updated_at
        }
    
    # Leave Request Management
    def get_leave_requests(
        self, 
        staff_id: Optional[UUID] = None, 
        status_filter: Optional[str] = None
    ) -> List[dict]:
        """Get leave requests with filters"""
        # LeaveRequest is already imported at top
        
        query = self.db.query(LeaveRequest).options(
            joinedload(LeaveRequest.staff),
            joinedload(LeaveRequest.manager)
        )
        
        if staff_id:
            query = query.filter(LeaveRequest.staff_id == staff_id)
        
        if status_filter:
            query = query.filter(LeaveRequest.status == status_filter)
        
        requests = query.order_by(LeaveRequest.submitted_at.desc()).all()
        
        return [
            {
                "id": str(req.id),
                "staff_id": str(req.staff_id),
                "staff_name": req.staff.full_name,
                "leave_date": req.leave_date.isoformat(),
                "leave_type": req.leave_type,
                "reason": req.reason,
                "status": req.status,
                "rejection_reason": req.rejection_reason,
                "submitted_at": req.submitted_at,
                "reviewed_at": req.reviewed_at,
                "manager_name": req.manager.full_name if req.manager else None
            }
            for req in requests
        ]
    
    def create_leave_request(
        self, 
        request_data: LeaveRequestCreate, 
        staff_id: UUID
    ) -> dict:
        """Create new leave request"""
        # LeaveRequest is already imported at top
        
        # Check if leave date is in the future
        if request_data.leave_date <= date.today():
            raise ValueError("Leave date must be in the future")
        
        # Check for existing request on same date
        existing = self.db.query(LeaveRequest).filter(
            and_(
                LeaveRequest.staff_id == staff_id,
                LeaveRequest.leave_date == request_data.leave_date,
                LeaveRequest.status.in_(["pending", "approved"])
            )
        ).first()
        
        if existing:
            raise ValueError("Leave request already exists for this date")
        
        # Create new request
        request = LeaveRequest(
            staff_id=staff_id,
            leave_date=request_data.leave_date,
            leave_type=request_data.leave_type,
            reason=request_data.reason,
            status="pending"
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        return self._format_leave_request_response(request)
    
    def update_leave_request(
        self, 
        request_id: UUID, 
        request_data: LeaveRequestUpdate, 
        manager_id: UUID
    ) -> dict:
        """Update leave request status (approve/reject)"""
        # LeaveRequest is already imported at top
        
        request = self.db.query(LeaveRequest).filter(
            LeaveRequest.id == request_id
        ).first()
        
        if not request:
            raise ValueError("Leave request not found")
        
        if request.status != "pending":
            raise ValueError("Only pending requests can be updated")
        
        # Update request
        request.status = request_data.status
        request.manager_id = manager_id
        request.reviewed_at = datetime.utcnow()
        
        if request_data.rejection_reason:
            request.rejection_reason = request_data.rejection_reason
        
        self.db.commit()
        self.db.refresh(request)
        
        return self._format_leave_request_response(request)
    
    def _format_leave_request_response(self, request) -> dict:
        """Format leave request for response"""
        return {
            "id": str(request.id),
            "staff_id": str(request.staff_id),
            "staff_name": request.staff.full_name if request.staff else None,
            "leave_date": request.leave_date.isoformat(),
            "leave_type": request.leave_type,
            "reason": request.reason,
            "status": request.status,
            "rejection_reason": request.rejection_reason,
            "submitted_at": request.submitted_at,
            "reviewed_at": request.reviewed_at,
            "manager_name": request.manager.full_name if request.manager else None
        }
    
    # Check-in Management
    def get_checkins(self, status_filter: Optional[str] = None) -> List[dict]:
        """Get check-in requests"""
        # StaffCheckin is already imported at top
        
        query = self.db.query(StaffCheckin).options(
            joinedload(StaffCheckin.staff),
            joinedload(StaffCheckin.schedule)
        )
        
        if status_filter:
            query = query.filter(StaffCheckin.status == status_filter)
        
        checkins = query.order_by(StaffCheckin.checkin_time.desc()).all()
        
        return [
            {
                "id": str(checkin.id),
                "staff_id": str(checkin.staff_id),
                "staff_name": checkin.staff.full_name,
                "schedule_id": str(checkin.schedule_id),
                "checkin_time": checkin.checkin_time,
                "status": checkin.status,
                "location": checkin.location,
                "notes": checkin.notes,
                "approved_at": checkin.approved_at,
                "rejected_reason": checkin.rejected_reason
            }
            for checkin in checkins
        ]
    
    def create_checkin(
        self, 
        checkin_data: CheckinCreate, 
        staff_id: UUID
    ) -> dict:
        """Create check-in request"""
        # StaffCheckin is already imported at top, StaffSchedule
        
        # Verify schedule exists and belongs to staff
        schedule = self.db.query(StaffSchedule).filter(
            and_(
                StaffSchedule.id == checkin_data.schedule_id,
                StaffSchedule.staff_id == staff_id
            )
        ).first()
        
        if not schedule:
            raise ValueError("Schedule not found or doesn't belong to staff")
        
        # Check if already checked in for this schedule
        existing = self.db.query(StaffCheckin).filter(
            StaffCheckin.schedule_id == checkin_data.schedule_id
        ).first()
        
        if existing:
            raise ValueError("Already checked in for this schedule")
        
        # Create check-in
        checkin = StaffCheckin(
            staff_id=staff_id,
            schedule_id=checkin_data.schedule_id,
            location=checkin_data.location,
            notes=checkin_data.notes,
            status="pending"
        )
        
        self.db.add(checkin)
        self.db.commit()
        self.db.refresh(checkin)
        
        return self._format_checkin_response(checkin)
    
    def approve_checkin(self, checkin_id: UUID, manager_id: UUID) -> dict:
        """Approve check-in request"""
        # StaffCheckin is already imported at top
        
        checkin = self.db.query(StaffCheckin).filter(
            StaffCheckin.id == checkin_id
        ).first()
        
        if not checkin:
            raise ValueError("Check-in not found")
        
        if checkin.status != "pending":
            raise ValueError("Only pending check-ins can be approved")
        
        # Update check-in
        checkin.status = "approved"
        checkin.manager_id = manager_id
        checkin.approved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(checkin)
        
        return self._format_checkin_response(checkin)
    
    def reject_checkin(
        self, 
        checkin_id: UUID, 
        reason: str, 
        manager_id: UUID
    ) -> dict:
        """Reject check-in request"""
        # StaffCheckin is already imported at top
        
        checkin = self.db.query(StaffCheckin).filter(
            StaffCheckin.id == checkin_id
        ).first()
        
        if not checkin:
            raise ValueError("Check-in not found")
        
        if checkin.status != "pending":
            raise ValueError("Only pending check-ins can be rejected")
        
        # Update check-in
        checkin.status = "rejected"
        checkin.manager_id = manager_id
        checkin.rejected_reason = reason
        
        self.db.commit()
        self.db.refresh(checkin)
        
        return self._format_checkin_response(checkin)
    
    def _format_checkin_response(self, checkin) -> dict:
        """Format check-in for response"""
        return {
            "id": str(checkin.id),
            "staff_id": str(checkin.staff_id),
            "staff_name": checkin.staff.full_name if checkin.staff else None,
            "schedule_id": str(checkin.schedule_id),
            "checkin_time": checkin.checkin_time,
            "status": checkin.status,
            "location": checkin.location,
            "notes": checkin.notes,
            "approved_at": checkin.approved_at,
            "rejected_reason": checkin.rejected_reason
        }
    
    # Statistics Methods
    def get_staff_statistics(
        self, 
        staff_id: int, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """Get statistics for a specific staff member"""
        from datetime import timedelta, time as dt_time
        
        # Set default date range if not provided (last 3 months)
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=90)
        
        # Get all schedules for this staff in date range
        schedules = self.db.query(StaffSchedule).options(
            joinedload(StaffSchedule.shift)
        ).filter(
            and_(
                StaffSchedule.staff_id == staff_id,
                StaffSchedule.scheduled_date >= start_date,
                StaffSchedule.scheduled_date <= end_date
            )
        ).all()
        
        # Get daily login logs for this staff in date range
        login_logs = self.db.query(DailyLoginLog).filter(
            and_(
                DailyLoginLog.user_id == staff_id,
                DailyLoginLog.login_date >= start_date,
                DailyLoginLog.login_date <= end_date
            )
        ).all()
        
        # Create a map of login_date -> first_login_time
        login_map = {log.login_date: log.first_login_time for log in login_logs}
        
        # Count statistics
        on_time_count = 0
        late_count = 0
        
        for schedule in schedules:
            scheduled_date = schedule.scheduled_date
            if scheduled_date in login_map:
                login_datetime = login_map[scheduled_date]  # Already a datetime
                shift_start = schedule.shift.start_time
                
                # Extract time from login_datetime (handle timezone-aware)
                if login_datetime.tzinfo:
                    # Convert to UTC then extract time
                    login_time_utc = login_datetime.astimezone(dt_timezone.utc).time()
                else:
                    login_time_utc = login_datetime.time()
                
                # Get shift start time
                shift_start_time = shift_start
                
                # Calculate allowed time (shift start + 10 minutes)
                shift_start_minutes = shift_start_time.hour * 60 + shift_start_time.minute
                allowed_minutes = shift_start_minutes + 10
                
                # Convert login time to minutes for comparison
                login_minutes = login_time_utc.hour * 60 + login_time_utc.minute
                
                # Compare: on-time if login within 10 minutes of shift start
                if login_minutes <= allowed_minutes:
                    on_time_count += 1
                else:
                    late_count += 1
        
        # Count approved leave requests
        leave_count = self.db.query(LeaveRequest).filter(
            and_(
                LeaveRequest.staff_id == staff_id,
                LeaveRequest.status == 'approved',
                LeaveRequest.leave_date >= start_date,
                LeaveRequest.leave_date <= end_date
            )
        ).count()
        
        return {
            "staff_id": staff_id,
            "on_time_count": on_time_count,
            "late_count": late_count,
            "leave_count": leave_count,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    
    def get_department_statistics(
        self,
        department_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """Get aggregated statistics for all staff in a department"""
        from datetime import timedelta
        
        # Set default date range if not provided
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=90)
        
        # Get all staff in department
        staff_list = self.db.query(User).filter(
            and_(
                User.department_id == department_id,
                User.role == 'staff',
                User.is_active == True
            )
        ).all()
        
        # Calculate statistics for each staff
        staff_stats = []
        for staff in staff_list:
            stats = self.get_staff_statistics(staff.id, start_date, end_date)
            stats["staff_name"] = staff.full_name
            staff_stats.append(stats)
        
        # Find top performers
        most_on_time = max(staff_stats, key=lambda x: x["on_time_count"], default=None)
        most_late = max(staff_stats, key=lambda x: x["late_count"], default=None)
        most_leave = max(staff_stats, key=lambda x: x["leave_count"], default=None)
        
        return {
            "department_id": department_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "most_on_time": {
                "staff_id": most_on_time["staff_id"] if most_on_time else None,
                "staff_name": most_on_time["staff_name"] if most_on_time else None,
                "count": most_on_time["on_time_count"] if most_on_time else 0
            },
            "most_late": {
                "staff_id": most_late["staff_id"] if most_late else None,
                "staff_name": most_late["staff_name"] if most_late else None,
                "count": most_late["late_count"] if most_late else 0
            },
            "most_leave": {
                "staff_id": most_leave["staff_id"] if most_leave else None,
                "staff_name": most_leave["staff_name"] if most_leave else None,
                "count": most_leave["leave_count"] if most_leave else 0
            },
            "all_staff_stats": staff_stats
        }