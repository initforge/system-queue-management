from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship  
from sqlalchemy.sql import func

from ...shared.core.database import Base

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    code = Column(String(10), unique=True, nullable=False)
    qr_code_token = Column(String(255), unique=True, nullable=False)
    max_concurrent_customers = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="department")
    services = relationship("Service", back_populates="department")
    counters = relationship("Counter", back_populates="department")
    tickets = relationship("QueueTicket", back_populates="department")
    qr_codes = relationship("QRCode", back_populates="department")
