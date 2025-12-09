from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class StaffNotification(Base):
    __tablename__ = "staff_notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    complaint_id = Column(Integer, ForeignKey("ticket_complaints.id"), nullable=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=True)
    
    # Notification content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="complaint")  # complaint, announcement, alert
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    
    # Complaint details stored as JSON
    complaint_details = Column(JSON, nullable=True)
    
    # Status tracking
    is_read = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_notifications")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_notifications")
    complaint = relationship("TicketComplaint", back_populates="notifications")
    ticket = relationship("QueueTicket", back_populates="notifications")

    def __repr__(self):
        return f"<StaffNotification(id={self.id}, recipient_id={self.recipient_id}, title='{self.title}')>"