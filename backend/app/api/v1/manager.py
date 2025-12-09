# FastAPI Backend Router - Manager APIs

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.ticket import QueueTicket
from app.models.department import Department
from app.models.service import Service
from app.models.ticket_complaint import TicketComplaint

router = APIRouter(prefix="/manager", tags=["manager"])

@router.get("/stats/{department_id}")
async def get_department_stats(
    department_id: int,
    period: str = Query(default="today", regex="^(today|week|month|quarter)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get department statistics for manager dashboard"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Calculate date range
    now = datetime.now()
    if period == "today":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:  # quarter
        start_date = now - timedelta(days=90)
    
    # Total tickets in period
    total_tickets = db.query(Ticket).filter(
        and_(
            Ticket.department_id == department_id,
            Ticket.created_at >= start_date
        )
    ).count()
    
    # Completed tickets
    completed_tickets = db.query(Ticket).filter(
        and_(
            Ticket.department_id == department_id,
            Ticket.status == TicketStatus.completed,
            Ticket.created_at >= start_date
        )
    ).count()
    
    # Calculate average wait time
    avg_wait_result = db.execute(text("""
        SELECT AVG(EXTRACT(EPOCH FROM (called_at - created_at))/60) as avg_wait_minutes
        FROM tickets 
        WHERE department_id = :dept_id 
        AND called_at IS NOT NULL 
        AND created_at >= :start_date
    """), {"dept_id": department_id, "start_date": start_date}).first()
    
    avg_wait_time = round(avg_wait_result[0] or 0, 1)
    
    # Calculate average service time
    avg_service_result = db.execute(text("""
        SELECT AVG(EXTRACT(EPOCH FROM (completed_at - called_at))/60) as avg_service_minutes
        FROM tickets 
        WHERE department_id = :dept_id 
        AND completed_at IS NOT NULL 
        AND called_at IS NOT NULL
        AND created_at >= :start_date
    """), {"dept_id": department_id, "start_date": start_date}).first()
    
    avg_service_time = round(avg_service_result[0] or 0, 1)
    
    # Customer satisfaction from feedback
    satisfaction_result = db.execute(text("""
        SELECT AVG((service_rating + staff_rating + speed_rating) / 3.0) as avg_rating
        FROM feedback f
        JOIN tickets t ON f.ticket_id = t.id
        WHERE t.department_id = :dept_id
        AND f.created_at >= :start_date
    """), {"dept_id": department_id, "start_date": start_date}).first()
    
    customer_satisfaction = round(satisfaction_result[0] or 0, 1)
    
    return {
        "totalTickets": total_tickets,
        "completedTickets": completed_tickets,
        "avgWaitTime": avg_wait_time,
        "avgServiceTime": avg_service_time,
        "customerSatisfaction": customer_satisfaction
    }

@router.get("/staff/performance/{department_id}")
async def get_staff_performance(
    department_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get staff performance metrics for department"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    staff_list = db.query(User).filter(
        and_(
            User.department_id == department_id,
            User.role == "staff",
            User.is_active == True
        )
    ).all()
    
    performance_data = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for staff in staff_list:
        # Count tickets served today
        tickets_served = db.query(Ticket).filter(
            and_(
                Ticket.served_by_user_id == staff.id,
                Ticket.status == TicketStatus.completed,
                Ticket.completed_at >= today
            )
        ).count()
        
        # Average service time
        avg_service_result = db.execute(text("""
            SELECT AVG(EXTRACT(EPOCH FROM (completed_at - called_at))/60) as avg_service_minutes
            FROM tickets 
            WHERE served_by_user_id = :staff_id 
            AND completed_at IS NOT NULL 
            AND called_at IS NOT NULL
            AND completed_at >= :today
        """), {"staff_id": staff.id, "today": today}).first()
        
        avg_service_time = round(avg_service_result[0] or 0, 1)
        
        # Staff rating from feedback
        rating_result = db.execute(text("""
            SELECT AVG(staff_rating) as avg_rating
            FROM feedback f
            JOIN tickets t ON f.ticket_id = t.id
            WHERE t.served_by_user_id = :staff_id
            AND f.created_at >= :today
        """), {"staff_id": staff.id, "today": today}).first()
        
        rating = round(rating_result[0] or 0, 1)
        
        performance_data.append({
            "id": staff.id,
            "full_name": staff.full_name,
            "email": staff.email,
            "tickets_served": tickets_served,
            "avg_service_time": avg_service_time,
            "rating": rating,
            "is_online": True  # This would come from WebSocket connection tracking
        })
    
    return performance_data

@router.get("/complaints")
async def get_complaint_list(
    department_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of complaints for manager"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = db.query(
        Complaint.id,
        Complaint.ticket_id,
        Complaint.description,
        Complaint.severity,
        Complaint.status,
        Complaint.resolution_notes,
        Complaint.created_at,
        Ticket.ticket_number,
        Ticket.customer_name,
        Ticket.department_id
    ).join(Ticket, Complaint.ticket_id == Ticket.id)
    
    if department_id:
        query = query.filter(Ticket.department_id == department_id)
    
    if status:
        query = query.filter(Complaint.status == status)
    
    complaints = query.order_by(desc(Complaint.created_at)).limit(50).all()
    
    return [
        {
            "id": complaint.id,
            "ticket_id": complaint.ticket_id,
            "ticket_number": complaint.ticket_number,
            "customer_name": complaint.customer_name,
            "department_id": complaint.department_id,
            "description": complaint.description,
            "severity": complaint.severity,
            "status": complaint.status,
            "resolution_notes": complaint.resolution_notes,
            "created_at": complaint.created_at.isoformat()
        }
        for complaint in complaints
    ]

@router.put("/complaints/{complaint_id}/resolve")
async def resolve_complaint(
    complaint_id: int,
    resolution_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a complaint"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    complaint.status = "resolved"
    complaint.resolution_notes = resolution_data.get("resolution_notes", "")
    complaint.resolved_by_user_id = current_user.id
    complaint.resolved_at = datetime.now()
    
    db.commit()
    db.refresh(complaint)
    
    return {"message": "Complaint resolved successfully"}

@router.get("/feedback/stats")
async def get_feedback_stats(
    department_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feedback statistics"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = db.query(Feedback).join(Ticket, Feedback.ticket_id == Ticket.id)
    
    if department_id:
        query = query.filter(Ticket.department_id == department_id)
    
    total_feedbacks = query.count()
    
    # Count resolved complaints
    complaints_query = db.query(Complaint).join(Ticket, Complaint.ticket_id == Ticket.id)
    if department_id:
        complaints_query = complaints_query.filter(Ticket.department_id == department_id)
    
    resolved_complaints = complaints_query.filter(Complaint.status == "resolved").count()
    
    return {
        "total_feedbacks": total_feedbacks,
        "resolved_complaints": resolved_complaints
    }

@router.post("/reports/generate")
async def generate_report(
    report_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate various reports"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    report_type = report_data.get("type")
    department_id = report_data.get("department_id")
    period = report_data.get("period", "today")
    
    # This is a simplified report generation
    # In a real system, you'd generate actual reports (PDF, Excel, etc.)
    report = {
        "id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "title": f"Báo cáo {report_type} - {period}",
        "type": report_type,
        "department_id": department_id,
        "period": period,
        "created_at": datetime.now().isoformat(),
        "download_url": f"/api/reports/download/{report_type}_{period}.pdf"
    }
    
    return report

@router.get("/manager-info")
async def get_manager_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get manager dashboard info"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    # Recent complaints with joins
    recent_complaints_query = db.query(
        TicketComplaint,
        User.full_name.label('staff_name'),
        User.email.label('staff_email'),
        QueueTicket.ticket_number,
        Service.name.label('service_name'),
        Department.name.label('department_name')
    ).outerjoin(
        User, TicketComplaint.assigned_to == User.id
    ).outerjoin(
        QueueTicket, TicketComplaint.ticket_id == QueueTicket.id
    ).outerjoin(
        Service, QueueTicket.service_id == Service.id
    ).outerjoin(
        Department, QueueTicket.department_id == Department.id
    ).filter(
        TicketComplaint.assigned_to == current_user.id
    ).order_by(desc(TicketComplaint.created_at)).limit(10)
    
    recent_complaints = recent_complaints_query.all()

    complaints_data = []
    for row in recent_complaints:
        # SQLAlchemy Row object - access by index for models, by name for labels
        complaint = row[0]  # TicketComplaint object
        staff_name = row.staff_name  # Labeled field
        staff_email = row.staff_email  # Labeled field  
        ticket_number = row.ticket_number  # Labeled field
        service_name = row.service_name  # Labeled field
        department_name = row.department_name  # Labeled field
        
        complaints_data.append({
            "id": complaint.id,
            "ticket_id": complaint.ticket_id,
            "ticket_number": ticket_number,
            "customer_name": complaint.customer_name,
            "customer_phone": complaint.customer_phone,
            "customer_email": complaint.customer_email,
            "subject": complaint.complaint_text[:50] + "..." if len(complaint.complaint_text) > 50 else complaint.complaint_text,
            "content": complaint.complaint_text,
            "complaint_text": complaint.complaint_text,
            "category": "service",
            "status": complaint.status,
            "staff_name": staff_name,
            "staff_email": staff_email,
            "service_name": service_name,
            "department_name": department_name,
            "priority": "medium",
            "created_at": complaint.created_at.isoformat() if complaint.created_at else None
        })

    return {
        "manager_name": current_user.full_name,
        "manager_email": current_user.email,
        "department_id": current_user.department_id,
        "recent_complaints": complaints_data,
        "stats": {
            "total_complaints": len(complaints_data),
            "pending_complaints": len([c for c in complaints_data if c["status"] == "pending"]),
            "resolved_complaints": len([c for c in complaints_data if c["status"] == "resolved"])
        }
    }
