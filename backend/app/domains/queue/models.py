from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ...shared.core.database import Base

class TicketStatus(str, enum.Enum):
    WAITING = "waiting"
    CALLED = "called"
    SERVING = "serving"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class TicketPriority(str, enum.Enum):
    NORMAL = "normal"
    HIGH = "high"
    ELDERLY = "elderly"
    DISABLED = "disabled"
    VIP = "vip"

class FieldType(str, enum.Enum):
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    NUMBER = "number"
    DATE = "date"

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    estimated_duration = Column(Integer, default=15)  # minutes
    code = Column(String(20), unique=True, nullable=False)
    priority_level = Column(String(20), server_default='normal')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="services")
    form_fields = relationship("ServiceFormField", back_populates="service")
    tickets = relationship("QueueTicket", back_populates="service")

class ServiceFormField(Base):
    __tablename__ = "service_form_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    field_name = Column(String(50), nullable=False)
    field_type = Column(SQLEnum(FieldType), nullable=False)
    field_label = Column(String(100), nullable=False)
    placeholder = Column(String(255))
    is_required = Column(Boolean, default=False)
    field_options = Column(JSON)  # For select, radio, checkbox options
    validation_rules = Column(JSON)  # Custom validation rules
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    service = relationship("Service", back_populates="form_fields")

class Counter(Base):
    __tablename__ = "counters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships  
    department = relationship("Department", back_populates="counters")
    tickets = relationship("QueueTicket", back_populates="counter")

class QueueTicket(Base):
    __tablename__ = "queue_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(20), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(100))
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("users.id"))
    counter_id = Column(Integer, ForeignKey("counters.id"))
    status = Column(String(20), server_default='waiting')
    priority = Column(String(20), server_default='normal')
    queue_position = Column(Integer)
    form_data = Column(JSON)  # Customer submitted form data
    notes = Column(Text)  # Staff notes
    estimated_wait_time = Column(Integer)  # minutes
    created_at = Column(DateTime, default=func.now())
    submitted_at = Column(DateTime)
    called_at = Column(DateTime)
    served_at = Column(DateTime)
    completed_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    
    # Relationships
    service = relationship("Service", back_populates="tickets")
    department = relationship("Department", back_populates="tickets")
    staff = relationship("User", back_populates="tickets")
    counter = relationship("Counter", back_populates="tickets")
    service_sessions = relationship("ServiceSession", back_populates="ticket")
    feedback = relationship("Feedback", back_populates="ticket", uselist=False)
    complaints = relationship("Complaint", back_populates="ticket")

class QRCode(Base):
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    registration_url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="qr_codes")

class ServiceSession(Base):
    __tablename__ = "service_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime)
    service_duration = Column(Integer)  # minutes
    is_completed = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Relationships
    ticket = relationship("QueueTicket", back_populates="service_sessions")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)
    service_rating = Column(Integer)  # 1-5 scale
    staff_rating = Column(Integer)  # 1-5 scale
    wait_time_rating = Column(Integer)  # 1-5 scale
    overall_satisfaction = Column(Integer)  # 1-5 scale
    comments = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    ticket = relationship("QueueTicket", back_populates="feedback")

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)
    complaint_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, investigating, resolved
    resolution = Column(Text)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    ticket = relationship("QueueTicket", back_populates="complaints")
