from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Date, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .core.database import Base

# Enum definitions
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"

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

# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    counter_id = Column(Integer, ForeignKey("counters.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Relationships
    department = relationship("Department", back_populates="users")
    tickets = relationship("QueueTicket", back_populates="staff")
    
    # Schedule relationships
    staff_schedules = relationship("StaffSchedule", foreign_keys="StaffSchedule.staff_id", back_populates="staff")
    leave_requests = relationship("LeaveRequest", foreign_keys="LeaveRequest.staff_id", back_populates="staff")

# Department model
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

# Service model
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

# Service form field model
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

# Counter model
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

# Queue ticket model
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
    
    # Review/Rating fields
    service_rating = Column(Integer)  # 1-5 stars
    staff_rating = Column(Integer)   # 1-5 stars
    speed_rating = Column(Integer)   # 1-5 stars
    overall_rating = Column(Integer) # 1-5 stars
    review_comments = Column(Text)   # User feedback text
    reviewed_at = Column(DateTime)   # When review was submitted
    
    # Relationships
    service = relationship("Service", back_populates="tickets")
    department = relationship("Department", back_populates="tickets")
    staff = relationship("User", back_populates="tickets")
    counter = relationship("Counter", back_populates="tickets")
    service_sessions = relationship("ServiceSession", back_populates="ticket")
    feedback = relationship("Feedback", back_populates="ticket", uselist=False)
    complaints = relationship("Complaint", back_populates="ticket")

# QR Code model
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

# Service session model
class ServiceSession(Base):
    __tablename__ = "service_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)
    counter_id = Column(Integer, ForeignKey("counters.id"))
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime)
    duration = Column(Integer)  # minutes
    status = Column(String(20), default="active")
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    # staff = relationship("User", back_populates="service_sessions")
    ticket = relationship("QueueTicket", back_populates="service_sessions")

# Feedback model
class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)
    service_rating = Column(Integer, nullable=False)  # 1-5 scale
    staff_rating = Column(Integer, nullable=False)    # 1-5 scale
    speed_rating = Column(Integer, nullable=False)    # 1-5 scale
    overall_rating = Column(Integer, nullable=False)  # 1-5 scale
    additional_comments = Column(Text)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    ticket = relationship("QueueTicket", back_populates="feedback")

# Complaint model
class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("queue_tickets.id"), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="minor")  # minor, major, critical
    status = Column(String(20), default="pending")  # pending, in_progress, resolved, dismissed
    is_anonymous = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    ticket = relationship("QueueTicket", back_populates="complaints")
    resolver = relationship("User", foreign_keys=[resolved_by])

# System log model
class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=func.now())

# Announcement model
class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(String(50), default="info")
    target_audience = Column(String(50), default="all")
    department_id = Column(Integer, ForeignKey("departments.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# =====================================================
# SCHEDULE MANAGEMENT MODELS
# =====================================================

from sqlalchemy.dialects.postgresql import UUID, ENUM
import uuid

# Schedule-specific enums
shift_type_enum = ENUM('morning', 'afternoon', 'night', name='shift_type')
shift_status_enum = ENUM('scheduled', 'confirmed', 'cancelled', 'completed', name='shift_status')
leave_type_enum = ENUM('sick', 'personal', 'vacation', 'emergency', name='leave_type')
leave_status_enum = ENUM('pending', 'approved', 'rejected', name='leave_status')
exchange_status_enum = ENUM('pending', 'approved', 'rejected', 'cancelled', name='exchange_status')
checkin_status_enum = ENUM('pending', 'approved', 'rejected', name='checkin_status')

class Shift(Base):
    __tablename__ = "shifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    shift_type = Column(shift_type_enum, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    schedules = relationship("StaffSchedule", back_populates="shift")

class StaffSchedule(Base):
    __tablename__ = "staff_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    shift_id = Column(UUID(as_uuid=True), ForeignKey('shifts.id'), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    status = Column(shift_status_enum, default='scheduled')
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id], back_populates="staff_schedules")
    manager = relationship("User", foreign_keys=[manager_id])
    shift = relationship("Shift", back_populates="schedules")
    checkins = relationship("StaffCheckin", back_populates="schedule")
    attendance = relationship("StaffAttendance", back_populates="schedule", uselist=False)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'))
    leave_date = Column(Date, nullable=False)
    leave_type = Column(leave_type_enum, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(leave_status_enum, default='pending')
    rejection_reason = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id], back_populates="leave_requests")
    manager = relationship("User", foreign_keys=[manager_id])

class ShiftExchange(Base):
    __tablename__ = "shift_exchanges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requesting_staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'))
    requesting_schedule_id = Column(UUID(as_uuid=True), ForeignKey('staff_schedules.id'), nullable=False)
    target_schedule_id = Column(UUID(as_uuid=True), ForeignKey('staff_schedules.id'), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(exchange_status_enum, default='pending')
    rejection_reason = Column(Text)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    requesting_staff = relationship("User", foreign_keys=[requesting_staff_id])
    target_staff = relationship("User", foreign_keys=[target_staff_id])
    manager = relationship("User", foreign_keys=[manager_id])
    requesting_schedule = relationship("StaffSchedule", foreign_keys=[requesting_schedule_id])
    target_schedule = relationship("StaffSchedule", foreign_keys=[target_schedule_id])

class StaffCheckin(Base):
    __tablename__ = "staff_checkins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('staff_schedules.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'))
    checkin_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(checkin_status_enum, default='pending')
    location = Column(Text)
    notes = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    rejected_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id])
    manager = relationship("User", foreign_keys=[manager_id])
    schedule = relationship("StaffSchedule", back_populates="checkins")

class StaffAttendance(Base):
    __tablename__ = "staff_attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    schedule_id = Column(UUID(as_uuid=True), ForeignKey('staff_schedules.id'), nullable=False)
    checkin_time = Column(DateTime(timezone=True))
    checkout_time = Column(DateTime(timezone=True))
    break_start_time = Column(DateTime(timezone=True))
    break_end_time = Column(DateTime(timezone=True))
    total_hours = Column(String(10))
    overtime_hours = Column(String(10), default='0')
    is_absent = Column(Boolean, default=False)
    absence_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    staff = relationship("User", foreign_keys=[staff_id])
    schedule = relationship("StaffSchedule", back_populates="attendance")

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

# AI Conversation Model
class AIConversation(Base):
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    conversation_id = Column(String(100), nullable=False, index=True)  # UUID for conversation grouping
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    context_data = Column(JSON)  # Store context when message was sent
    function_calls = Column(JSON)  # Store function calls if any
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])

# Knowledge Base Models
class KnowledgeBaseCategory(Base):
    __tablename__ = "knowledge_base_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon = Column(String(50))
    parent_id = Column(Integer, ForeignKey('knowledge_base_categories.id'))
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent = relationship("KnowledgeBaseCategory", remote_side=[id], backref="children")
    articles = relationship("KnowledgeBaseArticle", back_populates="category")

class KnowledgeBaseArticle(Base):
    __tablename__ = "knowledge_base_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey('knowledge_base_categories.id'))
    author_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    tags = Column(JSON, default=[])  # Array of tag strings
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    rating = Column(String(10), default='0')  # Store as string or use Numeric
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])
    department = relationship("Department", foreign_keys=[department_id])
    category = relationship("KnowledgeBaseCategory", back_populates="articles")
    attachments = relationship("KnowledgeBaseAttachment", back_populates="article", cascade="all, delete-orphan")

class KnowledgeBaseAttachment(Base):
    __tablename__ = "knowledge_base_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey('knowledge_base_articles.id', ondelete='CASCADE'), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(Text, nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    cloudinary_public_id = Column(String(255))
    uploaded_by = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("KnowledgeBaseArticle", back_populates="attachments")
    uploader = relationship("User", foreign_keys=[uploaded_by])
