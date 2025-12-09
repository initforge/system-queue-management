from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from .models import TicketStatus, TicketPriority

# Service schemas
class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: int
    estimated_duration: int = 15
    code: str
    priority_level: str = "normal"

class ServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    department_id: int
    estimated_duration: int
    code: str
    priority_level: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Ticket schemas
class TicketCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    service_id: int
    department_id: int
    form_data: Optional[Dict[str, Any]] = None

class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    customer_name: str
    customer_phone: str
    status: str
    priority: str
    queue_position: Optional[int]
    estimated_wait_time: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    staff_id: Optional[int] = None
    counter_id: Optional[int] = None
    notes: Optional[str] = None

# Feedback schemas
class FeedbackCreate(BaseModel):
    ticket_id: int
    service_rating: int
    staff_rating: int
    wait_time_rating: int
    overall_satisfaction: int
    comments: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    service_rating: int
    staff_rating: int
    wait_time_rating: int
    overall_satisfaction: int
    comments: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True