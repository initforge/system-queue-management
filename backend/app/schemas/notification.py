from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str = "complaint"
    priority: str = "normal"
    complaint_details: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    recipient_id: int
    sender_id: Optional[int] = None
    complaint_id: Optional[int] = None
    ticket_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None


class NotificationResponse(NotificationBase):
    id: int
    recipient_id: int
    sender_id: Optional[int] = None
    complaint_id: Optional[int] = None
    ticket_id: Optional[int] = None
    is_read: bool
    is_archived: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    notifications: list[NotificationResponse]
    total_count: int
    unread_count: int