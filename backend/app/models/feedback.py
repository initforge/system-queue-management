"""
Feedback Model - Customer feedback for tickets
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class Feedback(Base):
    """Customer feedback for service tickets"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=True)
    customer_name = Column(String(100), nullable=True)
    customer_email = Column(String(100), nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 rating
    category = Column(String(50), nullable=True)
    message = Column(Text, nullable=False)
    staff_response = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=False, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    responded_at = Column(DateTime, nullable=True)
    
    # Relationships
    ticket = relationship("QueueTicket", back_populates="feedback")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, ticket_id={self.ticket_id}, rating={self.rating})>"
        
        return sum(ratings) / len(ratings) if ratings else 0
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "overall_rating": self.overall_rating,
            "service_rating": self.service_rating,
            "staff_rating": self.staff_rating,
            "wait_time_rating": self.wait_time_rating,
            "additional_comments": self.additional_comments,
            "is_anonymous": self.is_anonymous,
            "average_rating": self.average_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }