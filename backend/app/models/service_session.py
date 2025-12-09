from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class ServiceSession(Base):
    __tablename__ = "service_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)
    counter_id = Column(Integer, ForeignKey("counters.id"))
    started_at = Column(DateTime, server_default=func.now())
    ended_at = Column(DateTime)
    duration = Column(Integer)  # minutes
    status = Column(String(20), default="active")
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    ticket = relationship("QueueTicket", back_populates="service_sessions")
