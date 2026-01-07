from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime, time
from uuid import UUID
from enum import Enum

# Enums
class ShiftType(str, Enum):
    morning = "morning"
    afternoon = "afternoon"
    night = "night"

class ShiftStatus(str, Enum):
    scheduled = "scheduled"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class LeaveType(str, Enum):
    sick = "sick"
    personal = "personal"
    vacation = "vacation"
    emergency = "emergency"

class LeaveStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class CheckinStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

# Shift Schemas
class ShiftBase(BaseModel):
    name: str = Field(..., description="Shift name")
    shift_type: ShiftType = Field(..., description="Type of shift")
    start_time: time = Field(..., description="Shift start time")
    end_time: time = Field(..., description="Shift end time")
    description: Optional[str] = Field(None, description="Shift description")

class ShiftCreate(ShiftBase):
    pass

class ShiftResponse(ShiftBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schedule Schemas
class ScheduleBase(BaseModel):
    staff_id: int = Field(..., description="Staff member ID")
    shift_id: UUID = Field(..., description="Shift ID")
    scheduled_date: date = Field(..., description="Date of scheduled work")
    notes: Optional[str] = Field(None, description="Additional notes")

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    status: Optional[ShiftStatus] = Field(None, description="Schedule status")
    notes: Optional[str] = Field(None, description="Additional notes")

class ScheduleResponse(ScheduleBase):
    id: UUID
    manager_id: int
    status: ShiftStatus
    created_at: datetime
    updated_at: datetime
    
    # Related data
    staff_name: Optional[str] = Field(None, description="Staff member name")
    staff_username: Optional[str] = Field(None, description="Staff member username")
    staff_email: Optional[str] = Field(None, description="Staff member email")
    shift_name: Optional[str] = Field(None, description="Shift name")
    shift_type: Optional[ShiftType] = Field(None, description="Shift type")
    start_time: Optional[str] = Field(None, description="Shift start time")
    end_time: Optional[str] = Field(None, description="Shift end time")

    class Config:
        from_attributes = True

# Leave Request Schemas
class LeaveRequestBase(BaseModel):
    leave_date: date = Field(..., description="Date of leave")
    leave_type: LeaveType = Field(..., description="Type of leave")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for leave")

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveRequestUpdate(BaseModel):
    status: LeaveStatus = Field(..., description="Leave request status")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")

class LeaveRequestResponse(LeaveRequestBase):
    id: UUID
    staff_id: int
    manager_id: Optional[int]
    status: LeaveStatus
    rejection_reason: Optional[str]
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    staff_name: Optional[str] = Field(None, description="Staff member name")
    manager_name: Optional[str] = Field(None, description="Manager name")

    class Config:
        from_attributes = True

# Shift Exchange Schemas
class ShiftExchangeBase(BaseModel):
    target_staff_id: UUID = Field(..., description="Target staff member ID")
    requesting_schedule_id: UUID = Field(..., description="Requesting staff's schedule ID")
    target_schedule_id: UUID = Field(..., description="Target staff's schedule ID")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for exchange")

class ShiftExchangeCreate(ShiftExchangeBase):
    pass

class ShiftExchangeResponse(ShiftExchangeBase):
    id: UUID
    requesting_staff_id: int
    manager_id: Optional[int]
    status: str  # exchange_status enum
    rejection_reason: Optional[str]
    requested_at: datetime
    reviewed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    requesting_staff_name: Optional[str] = Field(None, description="Requesting staff name")
    target_staff_name: Optional[str] = Field(None, description="Target staff name")

    class Config:
        from_attributes = True

# Check-in Schemas
class CheckinBase(BaseModel):
    schedule_id: UUID = Field(..., description="Schedule ID")
    location: Optional[str] = Field(None, description="Check-in location")
    notes: Optional[str] = Field(None, description="Additional notes")

class CheckinCreate(CheckinBase):
    pass

class CheckinResponse(CheckinBase):
    id: UUID
    staff_id: int
    manager_id: Optional[int]
    checkin_time: datetime
    status: CheckinStatus
    approved_at: Optional[datetime]
    rejected_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Related data
    staff_name: Optional[str] = Field(None, description="Staff member name")
    shift_name: Optional[str] = Field(None, description="Shift name")
    scheduled_date: Optional[date] = Field(None, description="Scheduled date")

    class Config:
        from_attributes = True

# Bulk Schedule Operations
class BulkScheduleCreate(BaseModel):
    schedules: List[ScheduleCreate] = Field(..., description="List of schedules to create")

class BulkScheduleResponse(BaseModel):
    created_count: int = Field(..., description="Number of schedules created")
    failed_count: int = Field(..., description="Number of failed creations")
    errors: List[str] = Field(default_factory=list, description="List of errors")

# Weekly Schedule Request
class WeeklyScheduleRequest(BaseModel):
    start_date: date = Field(..., description="Start date of the week")
    staff_id: Optional[UUID] = Field(None, description="Specific staff ID (optional)")

# Dashboard Statistics
class ScheduleStats(BaseModel):
    total_staff: int = Field(..., description="Total staff count")
    scheduled_today: int = Field(..., description="Staff scheduled today")
    pending_checkins: int = Field(..., description="Pending check-in requests")
    pending_leave_requests: int = Field(..., description="Pending leave requests")
    upcoming_shifts: int = Field(..., description="Upcoming shifts this week")

class StaffScheduleStats(BaseModel):
    total_shifts_this_week: int = Field(..., description="Total shifts this week")
    completed_shifts: int = Field(..., description="Completed shifts")
    upcoming_shifts: int = Field(..., description="Upcoming shifts")
    pending_leave_requests: int = Field(..., description="Pending leave requests")
    attendance_rate: float = Field(..., description="Attendance rate percentage")