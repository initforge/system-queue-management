"""
Service Schemas - Simple version for login to work
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class FieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    SELECT = "select"
    TEXTAREA = "textarea"
    DATE = "date"
    CHECKBOX = "checkbox"

class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    estimated_duration: int = 15
    is_active: bool = True
    department_id: int

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_duration: Optional[int] = None
    is_active: Optional[bool] = None
    department_id: Optional[int] = None

class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}

class ServiceFormField(BaseModel):
    id: int
    service_id: int
    field_name: str
    field_type: FieldType
    field_label: str
    placeholder: Optional[str] = None
    is_required: bool = True
    field_options: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    display_order: int = 0
    
    model_config = {"from_attributes": True}

class ServiceWithFormFields(ServiceResponse):
    form_fields: List[ServiceFormField] = []
