from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ...shared.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager" 
    STAFF = "staff"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    counter_id = Column(Integer, ForeignKey("counters.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Relationships - will be defined when all domains are set up
    department = relationship("Department", back_populates="users")
    tickets = relationship("QueueTicket", back_populates="staff")
    staff_schedules = relationship("StaffSchedule", foreign_keys="StaffSchedule.staff_id", back_populates="staff")
    leave_requests = relationship("LeaveRequest", foreign_keys="LeaveRequest.staff_id", back_populates="staff")
