from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default='general')  # general, urgent, maintenance
    target_audience = Column(String(50), default='all')  # all, staff, customers
    department_id = Column(Integer, ForeignKey("departments.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    starts_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    department = relationship("Department")
    author = relationship("User")
