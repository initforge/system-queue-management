from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response schema for all API responses"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class ErrorResponse(BaseResponse):
    """Error response schema"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Any] = None

class SuccessResponse(BaseResponse):
    """Success response schema with data"""
    data: Optional[Any] = None

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    size: int
    total: int
    pages: int

class PaginatedResponse(BaseResponse):
    """Paginated response schema"""
    data: list
    meta: PaginationMeta