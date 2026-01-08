from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class StaffPerformance(Base):
    __tablename__ = "staff_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    date = Column(Date, nullable=False)
    tickets_served = Column(Integer, default=0)
    avg_service_time = Column(Numeric(5,2), default=0)
    total_rating_score = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)
    avg_rating = Column(Numeric(3,2), default=0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User")
    department = relationship("Department")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_staff_perf_user_date'),
    )
