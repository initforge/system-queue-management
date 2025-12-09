# Standard Response Schemas
from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime

# Base Response Schema
class BaseResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime = datetime.now()

# Success Response Schema
class SuccessResponse(BaseResponse):
    success: bool = True
    data: Optional[Any] = None

# Error Response Schema
class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[dict] = None

# Paginated Response Schema
class PaginatedResponse(BaseResponse):
    success: bool = True
    data: List[Any]
    pagination: dict
    
    @classmethod
    def create(
        cls,
        data: List[Any],
        page: int,
        per_page: int,
        total: int,
        message: str = "Data retrieved successfully"
    ):
        total_pages = (total + per_page - 1) // per_page
        return cls(
            message=message,
            data=data,
            pagination={
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        )

# API Health Response
class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = datetime.now()
    version: str
    database: str = "connected"
    redis: str = "connected"
    
# Statistics Response
class StatsResponse(BaseModel):
    period: str
    data: dict
    generated_at: datetime = datetime.now()

# File Upload Response
class FileUploadResponse(BaseResponse):
    success: bool = True
    file_url: str
    file_name: str
    file_size: int
    content_type: str