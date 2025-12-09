from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    code = Column(String, unique=True, index=True)
    qr_code_token = Column(String, unique=True)
    max_concurrent_customers = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    services = relationship("Service", back_populates="department")
    staff = relationship("User", back_populates="department")
    tickets = relationship("QueueTicket", back_populates="department")
    qr_codes = relationship("QRCode", back_populates="department")