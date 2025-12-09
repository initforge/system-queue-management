"""
Queue Ticket management services
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..models.ticket import QueueTicket, TicketStatus
from ..models.service import Service
from ..models.department import Department

def create_ticket(
    db: Session,
    service_id: int,
    customer_name: str,
    customer_phone: Optional[str] = None,
    customer_email: Optional[str] = None,
    department_id: Optional[int] = None,
    notes: Optional[str] = None
) -> QueueTicket:
    # Get service and department info
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise ValueError("Service not found")
        
    # Generate ticket number - Bank style A,B,C,D based on department ID
    dept_prefixes = {
        1: "A",  # Phòng Kế hoạch Tổng hợp
        2: "B",  # Phòng Tài chính Kế toán  
        3: "C",  # Phòng Hành chính Quản trị
        4: "D",  # Phòng Công nghệ Thông tin
    }
    
    dept_prefix = dept_prefixes.get(service.department_id, "X")
    
    # Find the highest bank-format ticket number for this prefix (globally unique)
    # Since ticket_number must be unique across all departments
    from sqlalchemy import text
    result = db.execute(text("""
        SELECT ticket_number FROM queue_tickets 
        WHERE ticket_number ~ :pattern
        ORDER BY ticket_number DESC
        LIMIT 1
    """), {
        "pattern": f"^{dept_prefix}[0-9]{{3}}$"
    }).fetchone()
    
    if result:
        # Extract number from last ticket (e.g., "A005" -> 5)
        last_number = int(result[0][1:])  # Remove first character, convert to int
        next_number = last_number + 1
    else:
        # No bank-format tickets with this prefix ever, start from 1
        next_number = 1
    
    ticket_number = f"{dept_prefix}{next_number:03d}"
    
    # Create ticket
    ticket = QueueTicket(
        ticket_number=ticket_number,
        customer_name=customer_name,
        customer_phone=customer_phone,
        service_id=service_id,
        department_id=service.department_id,
        notes=notes,
        estimated_wait_time=service.estimated_duration,
        status=TicketStatus.waiting
    )
    
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def get_ticket(db: Session, ticket_id: int) -> Optional[QueueTicket]:
    return db.query(QueueTicket).filter(QueueTicket.id == ticket_id).first()

def get_ticket_by_number(db: Session, ticket_number: str) -> Optional[QueueTicket]:
    return db.query(QueueTicket).filter(QueueTicket.ticket_number == ticket_number).first()

def get_department_queue(db: Session, department_id: int, status: Optional[TicketStatus] = None) -> List[QueueTicket]:
    query = db.query(QueueTicket).filter(QueueTicket.department_id == department_id)
    if status:
        query = query.filter(QueueTicket.status == status)
    return query.order_by(QueueTicket.created_at).all()

def update_ticket_status(
    db: Session,
    ticket_id: int,
    new_status: TicketStatus,
    staff_id: Optional[int] = None
) -> Optional[QueueTicket]:
    ticket = db.query(QueueTicket).filter(QueueTicket.id == ticket_id).first()
    if not ticket:
        return None
        
    ticket.status = new_status
    
    if new_status == TicketStatus.called:
        ticket.called_at = datetime.utcnow()
        ticket.staff_id = staff_id
    elif new_status == TicketStatus.completed:
        ticket.serving_started_at = datetime.utcnow()
    elif new_status in [TicketStatus.completed, TicketStatus.no_show]:
        ticket.completed_at = datetime.utcnow()
        
    db.commit()
    db.refresh(ticket)
    return ticket

def get_next_ticket(db: Session, department_id: int, staff_id: int) -> Optional[QueueTicket]:
    next_ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.department_id == department_id,
            QueueTicket.status == TicketStatus.waiting
        )
    ).order_by(QueueTicket.created_at).first()
    
    if next_ticket:
        next_ticket = update_ticket_status(db, next_ticket.id, TicketStatus.called, staff_id)
        
    return next_ticket
