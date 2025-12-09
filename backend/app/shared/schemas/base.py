from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TimestampMixin(BaseModel):
    """Base mixin for timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None

class IdMixin(BaseModel):
    """Base mixin for ID field"""
    id: int

class BaseEntity(IdMixin, TimestampMixin):
    """Base entity with ID and timestamps"""
    pass
