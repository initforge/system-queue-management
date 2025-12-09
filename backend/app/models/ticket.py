from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..core.database import Base

class TicketStatus(str, enum.Enum):
    waiting = "waiting"
    called = "called"
    completed = "completed"
    no_show = "no_show"

class TicketPriority(str, enum.Enum):
    NORMAL = "normal"
    HIGH = "high"
    ELDERLY = "elderly"
    DISABLED = "disabled"
    VIP = "vip"

class QueueTicket(Base):
    __tablename__ = "queue_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True)
    customer_name = Column(String)
    customer_phone = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.waiting)
    queue_position = Column(Integer, nullable=True)  # Position in queue
    notes = Column(Text, nullable=True)
    estimated_wait_time = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    called_at = Column(DateTime, nullable=True)
    served_at = Column(DateTime, nullable=True)  # Changed from serving_started_at
    completed_at = Column(DateTime, nullable=True)
    
    # Rating and review fields (from database schema)
    service_rating = Column(Integer, nullable=True)  # 1-5 stars
    staff_rating = Column(Integer, nullable=True)    # 1-5 stars  
    speed_rating = Column(Integer, nullable=True)    # 1-5 stars
    overall_rating = Column(Integer, nullable=True)  # 1-5 stars
    review_comments = Column(Text, nullable=True)    # Customer feedback
    reviewed_at = Column(DateTime, nullable=True)    # When review was submitted

    # Relationships
    service = relationship("Service", back_populates="tickets")
    department = relationship("Department", back_populates="tickets")
    staff = relationship("User", back_populates="tickets_handled")
    ticket_complaints = relationship("TicketComplaint", back_populates="ticket")
    feedback = relationship("Feedback", back_populates="ticket")
    notifications = relationship("StaffNotification", back_populates="ticket")
    service_sessions = relationship("ServiceSession", back_populates="ticket")