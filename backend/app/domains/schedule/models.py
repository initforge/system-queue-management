from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid
import enum

from ...shared.core.database import Base

class ShiftType(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"

class ShiftStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class LeaveType(str, enum.Enum):
    SICK = "sick"
    PERSONAL = "personal"
    VACATION = "vacation"
    EMERGENCY = "emergency"

class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ExchangeStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class CheckinStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    shift_type = Column(String(20), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    schedules = relationship("StaffSchedule", back_populates="shift")

class StaffSchedule(Base):
    __tablename__ = "staff_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shift_id = Column(UUID(as_uuid=True), ForeignKey('shifts.id'), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    status = Column(String(20), default='scheduled')
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id], back_populates="staff_schedules")
    manager = relationship("User", foreign_keys=[manager_id])
    shift = relationship("Shift", back_populates="schedules")
    checkins = relationship("StaffCheckin", back_populates="schedule")
    attendance = relationship("StaffAttendance", back_populates="schedule", uselist=False)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'))
    leave_date = Column(Date, nullable=False)
    leave_type = Column(String(20), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default='pending')
    rejection_reason = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id], back_populates="leave_requests")
    manager = relationship("User", foreign_keys=[manager_id])

class ShiftExchange(Base):
    __tablename__ = "shift_exchanges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requesting_staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'))
    requesting_schedule_id = Column(UUID(as_uuid=True), ForeignKey('staff_schedules.id'), nullable=False)
    target_schedule_id = Column(UUID(as_uuid=True), ForeignKey('staff_schedules.id'), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), default='pending')
    rejection_reason = Column(Text)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    requesting_staff = relationship("User", foreign_keys=[requesting_staff_id])
    target_staff = relationship("User", foreign_keys=[target_staff_id])
    manager = relationship("User", foreign_keys=[manager_id])
    requesting_schedule = relationship("StaffSchedule", foreign_keys=[requesting_schedule_id])
    target_schedule = relationship("StaffSchedule", foreign_keys=[target_schedule_id])

class StaffCheckin(Base):
    __tablename__ = "staff_checkins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('staff_schedules.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'))
    checkin_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default='pending')
    location = Column(Text)
    notes = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    rejected_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id])
    manager = relationship("User", foreign_keys=[manager_id])
    schedule = relationship("StaffSchedule", back_populates="checkins")

class StaffAttendance(Base):
    __tablename__ = "staff_attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('staff_schedules.id'), nullable=False)
    checkin_time = Column(DateTime(timezone=True))
    checkout_time = Column(DateTime(timezone=True))
    break_start_time = Column(DateTime(timezone=True))
    break_end_time = Column(DateTime(timezone=True))
    total_hours = Column(String(10))
    overtime_hours = Column(String(10), default='0')
    is_absent = Column(Boolean, default=False)
    absence_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id])
    schedule = relationship("StaffSchedule", back_populates="attendance")
