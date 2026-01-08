from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import JSONB
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
    normal = "normal"
    high = "high"
    elderly = "elderly"
    disabled = "disabled"
    vip = "vip"

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
    counter_id = Column(Integer, ForeignKey("counters.id"), nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.waiting)
    priority = Column(Enum(TicketPriority), default=TicketPriority.normal)
    queue_position = Column(Integer, nullable=True)
    form_data = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)
    estimated_wait_time = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    called_at = Column(DateTime, nullable=True)
    served_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Simplified rating (overall only)
    overall_rating = Column(Integer, nullable=True)
    review_comments = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    service = relationship("Service", back_populates="tickets")
    department = relationship("Department", back_populates="tickets")
    staff = relationship("User", back_populates="tickets_handled")
    counter = relationship("Counter", back_populates="tickets")
    ticket_complaints = relationship("TicketComplaint", back_populates="ticket")