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
    upcoming_shifts: int = Field(..., description="Upcoming shifts this week")

class StaffScheduleStats(BaseModel):
    total_shifts_this_week: int = Field(..., description="Total shifts this week")
    completed_shifts: int = Field(..., description="Completed shifts")
    upcoming_shifts: int = Field(..., description="Upcoming shifts")
    attendance_rate: float = Field(..., description="Attendance rate percentage")

# Leave Request Schemas (Placeholder for future implementation)
class LeaveRequestCreate(BaseModel):
    staff_id: int = Field(..., description="Staff member ID")
    start_date: date = Field(..., description="Leave start date")
    end_date: date = Field(..., description="Leave end date")
    reason: Optional[str] = Field(None, description="Reason for leave")

class LeaveRequestUpdate(BaseModel):
    status: Optional[str] = Field(None, description="Leave request status")
    reason: Optional[str] = Field(None, description="Reason for leave")

class LeaveRequestResponse(BaseModel):
    id: int
    staff_id: int
    start_date: date
    end_date: date
    reason: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Shift Exchange Schemas (Placeholder for future implementation)
class ShiftExchangeCreate(BaseModel):
    from_schedule_id: UUID = Field(..., description="Schedule ID to exchange from")
    to_staff_id: int = Field(..., description="Staff member ID to exchange with")
    reason: Optional[str] = Field(None, description="Reason for exchange")

class ShiftExchangeResponse(BaseModel):
    id: int
    from_schedule_id: UUID
    to_staff_id: int
    reason: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Check-in Schemas (Placeholder for future implementation)
class CheckinCreate(BaseModel):
    schedule_id: UUID = Field(..., description="Schedule ID")
    checkin_time: Optional[datetime] = Field(None, description="Check-in time")

class CheckinResponse(BaseModel):
    id: int
    schedule_id: UUID
    checkin_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True