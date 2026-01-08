"""
Ticket Complaint model for complaints sent to manager
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..core.database import Base

class TicketComplaintStatus(enum.Enum):
    waiting = "waiting"
    processing = "processing"
    completed = "completed"

class TicketComplaint(Base):
    __tablename__ = "ticket_complaints"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=True)
    customer_email = Column(String(100), nullable=True)
    complaint_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # Rating from review
    status = Column(String(20), default='waiting')  # waiting, processing, completed
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Manager ID
    manager_response = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    ticket = relationship("QueueTicket", back_populates="ticket_complaints") 
    assigned_manager = relationship("User", foreign_keys=[assigned_to])
