from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from ...core.database import get_db
from ...models import QueueTicket, User, Service, Department, TicketComplaint
from ...core.security import get_current_user, require_manager_or_admin
from pydantic import BaseModel, validator

router = APIRouter(prefix="/feedback", tags=["feedback"])

# Pydantic models for review (rating only)
class ReviewSubmit(BaseModel):
    ticket_number: str
    overall_rating: int
    review_comments: Optional[str] = None
    
    @validator('overall_rating')
    def validate_rating(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

# Complaint models
class ComplaintSubmit(BaseModel):
    ticket_number: str
    complaint_text: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

# Submit feedback
@router.post("/submit")
async def submit_review(
    review_data: ReviewSubmit,
    db: Session = Depends(get_db)
):
    """Submit customer review (rating only)"""
    
    # Find ticket by ticket_number
    ticket = db.query(QueueTicket).filter(QueueTicket.ticket_number == review_data.ticket_number).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Update ticket with rating
    ticket.overall_rating = review_data.overall_rating
    ticket.review_comments = review_data.review_comments
    ticket.reviewed_at = datetime.now()
    
    db.commit()
    db.refresh(ticket)
    
    return {
        "success": True,
        "message": "Review submitted successfully",
        "ticket_number": ticket.ticket_number,
        "rating": ticket.overall_rating
    }

# Submit complaint
@router.post("/complaint")
async def submit_complaint(
    complaint_data: ComplaintSubmit,
    db: Session = Depends(get_db)
):
    """Submit customer complaint"""
    
    # Find ticket by ticket_number
    ticket = db.query(QueueTicket).filter(QueueTicket.ticket_number == complaint_data.ticket_number).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # Create complaint
    complaint = TicketComplaint(
        ticket_id=ticket.id,
        complaint_text=complaint_data.complaint_text,
        customer_name=complaint_data.customer_name or ticket.customer_name,
        customer_email=complaint_data.customer_email or ticket.customer_email,
        status="waiting",
        created_at=datetime.now()
    )
    
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    
    return {
        "success": True,
        "message": "Complaint submitted successfully",
        "complaint_id": complaint.id,
        "ticket_number": ticket.ticket_number
    }