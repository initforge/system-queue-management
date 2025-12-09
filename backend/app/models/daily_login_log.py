from sqlalchemy import Column, Integer, String, Date, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class DailyLoginLog(Base):
    __tablename__ = "daily_login_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    login_date = Column(Date, nullable=False)
    first_login_time = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        UniqueConstraint('user_id', 'login_date', name='uq_user_daily_login'),
    )
