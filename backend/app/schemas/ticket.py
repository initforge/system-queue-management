# Ticket Pydantic Schemas
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

# Import enums from models to ensure consistency
from ..models.ticket import TicketStatus, TicketPriority

# Base Ticket Schema
class TicketBase(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    service_id: int
    department_id: int
    priority: TicketPriority = TicketPriority.normal
    notes: Optional[str] = None

# Ticket Creation Schema
class TicketCreate(TicketBase):
    @validator('customer_name')
    def validate_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Customer name must be at least 2 characters long')
        return v.strip()

# Ticket Update Schema
class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    notes: Optional[str] = None
    completion_notes: Optional[str] = None
    served_by_user_id: Optional[int] = None

# Ticket Status Update Schema (for simpler status changes)
class TicketStatusUpdate(BaseModel):
    status: TicketStatus
    notes: Optional[str] = None

# Ticket Response Schema
class TicketResponse(TicketBase):
    id: int
    ticket_number: str
    queue_number: int
    status: TicketStatus
    created_at: datetime
    called_at: Optional[datetime] = None
    serving_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    served_by_user_id: Optional[int] = None
    
    # Related data
    service_name: Optional[str] = None
    department_name: Optional[str] = None
    served_by_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Queue Status Schema
class QueueStatus(BaseModel):
    ticket_id: int
    ticket_number: str
    customer_name: str
    service_name: str
    status: TicketStatus
    queue_position: int
    estimated_wait_time: int  # in minutes
    created_at: datetime
    
    class Config:
        from_attributes = True

# Ticket Statistics Schema
class TicketStats(BaseModel):
    total_tickets: int
    waiting_tickets: int
    serving_tickets: int
    completed_tickets: int
    average_wait_time: float  # in minutes
    average_service_time: float  # in minutes