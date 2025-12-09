from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    role = Column(String)  # admin, manager, staff
    department_id = Column(Integer, ForeignKey("departments.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    department = relationship("Department", back_populates="staff")
    tickets_handled = relationship("QueueTicket", back_populates="staff")
    
    # Notification relationships
    received_notifications = relationship("StaffNotification", foreign_keys="StaffNotification.recipient_id", back_populates="recipient")
    sent_notifications = relationship("StaffNotification", foreign_keys="StaffNotification.sender_id", back_populates="sender")
    
    # Schedule relationships
    staff_schedules = relationship("StaffSchedule", foreign_keys="StaffSchedule.staff_id", back_populates="staff")
    leave_requests = relationship("LeaveRequest", foreign_keys="LeaveRequest.staff_id", back_populates="staff")