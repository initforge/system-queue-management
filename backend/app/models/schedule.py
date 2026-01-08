from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid

from ..core.database import Base

# Schedule-specific enums
shift_type_enum = ENUM('morning', 'afternoon', 'night', name='shift_type')
shift_status_enum = ENUM('scheduled', 'confirmed', 'cancelled', 'completed', name='shift_status')


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    shift_type = Column(shift_type_enum, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    schedules = relationship("StaffSchedule", back_populates="shift")


class StaffSchedule(Base):
    __tablename__ = "staff_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shift_id = Column(UUID(as_uuid=True), ForeignKey('shifts.id'), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    status = Column(shift_status_enum, default='scheduled')
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id], back_populates="staff_schedules")
    manager = relationship("User", foreign_keys=[manager_id])
    shift = relationship("Shift", back_populates="schedules")
