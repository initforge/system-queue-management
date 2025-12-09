"""
Ticket management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...core.database import get_db
from ...core.security import get_current_user, require_active_user
from ...models import User, QueueTicket, Service, Department
from ...schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
    TicketStatusUpdate,
    TicketStatus,
    TicketPriority
)

router = APIRouter()

@router.post("/", response_model=TicketResponse)
def create_new_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db)
):
    """Create a new ticket"""
    try:
        print(f"Creating ticket with data: service_id={ticket_data.service_id}, dept_id={ticket_data.department_id}")
        
        ticket = create_ticket(
            db=db,
            service_id=ticket_data.service_id,
            customer_name=ticket_data.customer_name,
            customer_phone=ticket_data.customer_phone,
            department_id=ticket_data.department_id,
            notes=ticket_data.notes
        )
        
        print(f"Ticket created successfully: {ticket.id}")
        return ticket
    except ValueError as e:
        print(f"ValueError in ticket creation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in ticket creation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get ticket details"""
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy vé"
        )
    return ticket

@router.get("/number/{ticket_number}", response_model=TicketResponse)
def get_ticket_by_ticket_number(
    ticket_number: str,
    db: Session = Depends(get_db)
):
    """Get ticket by ticket number"""
    ticket = get_ticket_by_number(db, ticket_number)
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy vé"
        )
    return ticket

@router.get("/department/{department_id}", response_model=List[TicketResponse])
def get_department_tickets(
    department_id: int,
    status: Optional[TicketStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user)
):
    """Get all tickets for a department"""
    tickets = get_department_queue(db, department_id, status)
    return tickets
        
@router.put("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status_endpoint(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user)
):
    """Update ticket status"""
    updated_ticket = update_ticket_status(
        db=db,
        ticket_id=ticket_id,
        new_status=status_data.status,
        staff_id=current_user.id if status_data.status in [TicketStatus.CALLED, TicketStatus.SERVING] else None
    )
    if not updated_ticket:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy vé"
        )
    return updated_ticket

@router.post("/next", response_model=TicketResponse)
def get_next_ticket_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user)
):
    """Get next ticket in queue for current staff"""
    if not current_user.department_id:
        raise HTTPException(
            status_code=400,
            detail="Nhân viên chưa được phân công phòng ban"
        )
        
    next_ticket = get_next_ticket(db, current_user.department_id, current_user.id)
    if not next_ticket:
        raise HTTPException(
            status_code=404,
            detail="Không có vé đang chờ trong hàng đợi"
        )
    return next_ticket

# Helper function to generate ticket number
async def _generate_ticket_number(db: AsyncSession, department_id: int) -> str:
    """Generate unique ticket number in format: A001, B015, etc."""
    # Get department
    dept_result = await db.execute(select(Department).where(Department.id == department_id))
    dept = dept_result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Map department to letter prefix
    dept_prefixes = {1: "A", 2: "B", 3: "C", 4: "D"}
    dept_letter = dept_prefixes.get(department_id, "X")
    
    # Get max counter number for today (from all departments to ensure global uniqueness)
    today = datetime.now().date()
    max_ticket_result = await db.execute(
        select(QueueTicket)
        .where(func.date(QueueTicket.created_at) == today)
        .order_by(QueueTicket.ticket_number.desc())
        .limit(1)
    )
    max_ticket = max_ticket_result.scalar_one_or_none()
    
    max_counter = 0
    if max_ticket and max_ticket.ticket_number:
        try:
            # Extract highest number from any ticket today (e.g., "A005" -> 5, "B010" -> 10)
            import re
            numbers = re.findall(r'\d+', max_ticket.ticket_number)
            if numbers:
                max_counter = int(numbers[0])
        except (ValueError, IndexError):
            pass
    
    # Counter-style format: A001, B001, C001, D001 (Next available global number)
    counter_number = max_counter + 1
    ticket_number = f"{dept_letter}{counter_number:03d}"
    
    # Double-check uniqueness (safety net)
    while True:
        existing_result = await db.execute(select(QueueTicket).where(QueueTicket.ticket_number == ticket_number))
        if not existing_result.scalar_one_or_none():
            break
        counter_number += 1
        ticket_number = f"{dept_letter}{counter_number:03d}"
    
    return ticket_number

@router.post("/register", response_model=TicketResponse)
async def register_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db)
):
    # Get service and department info
    result = await db.execute(
        select(Service, Department)
        .join(Department)
        .where(Service.id == ticket_data.service_id)
        .options(selectinload(Service.department))
    )
    service_dept = result.first()
    
    if not service_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    
    service, department = service_dept
    
    # Generate ticket number
    ticket_number = await _generate_ticket_number(db, department.id)
    
    # Calculate queue position
    queue_count = await db.execute(
        select(func.count(QueueTicket.id))
        .where(
            and_(
                QueueTicket.department_id == department.id,
                QueueTicket.status.in_([TicketStatus.WAITING, TicketStatus.CALLED])
            )
        )
    )
    queue_position = queue_count.scalar() + 1
    
    # Create ticket
    new_ticket = QueueTicket(
        ticket_number=ticket_number,
        customer_name=ticket_data.customer_name,
        customer_phone=ticket_data.customer_phone,
        customer_email=ticket_data.customer_email,
        service_id=ticket_data.service_id,
        department_id=department.id,
        status=TicketStatus.WAITING,
        priority=ticket_data.priority,
        queue_position=queue_position,
        form_data=ticket_data.form_data,
        submitted_at=datetime.utcnow(),
        estimated_wait_time=queue_position * service.estimated_duration
    )
    
    db.add(new_ticket)
    await db.commit()
    await db.refresh(new_ticket)
    
    return TicketResponse(
        id=new_ticket.id,
        ticket_number=new_ticket.ticket_number,
        customer_name=new_ticket.customer_name,
        customer_phone=new_ticket.customer_phone,
        customer_email=new_ticket.customer_email,
        service_id=new_ticket.service_id,
        service_name=service.name,
        department_id=new_ticket.department_id,
        department_name=department.name,
        status=new_ticket.status,
        priority=new_ticket.priority,
        queue_position=new_ticket.queue_position,
        form_data=new_ticket.form_data,
        notes=new_ticket.notes,
        estimated_wait_time=new_ticket.estimated_wait_time,
        created_at=new_ticket.created_at,
        called_at=new_ticket.called_at,
        served_at=new_ticket.served_at,
        completed_at=new_ticket.completed_at
    )

@router.get("/status/{ticket_number}", response_model=TicketResponse)
async def get_ticket_status(
    ticket_number: str,
    db: AsyncSession = Depends(get_db)
):
    # Get ticket with service and department info
    result = await db.execute(
        select(QueueTicket, Service, Department)
        .join(Service)
        .join(Department)
        .where(QueueTicket.ticket_number == ticket_number)
    )
    ticket_info = result.first()
    
    if not ticket_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ticket, service, department = ticket_info
    
    # Get current serving ticket
    current_serving_result = await db.execute(
        select(QueueTicket.ticket_number)
        .where(
            and_(
                QueueTicket.department_id == ticket.department_id,
                QueueTicket.status == TicketStatus.SERVING
            )
        )
        .limit(1)
    )
    current_serving = current_serving_result.scalar()
    
    # Count people ahead in queue
    people_ahead = await db.execute(
        select(func.count(QueueTicket.id))
        .where(
            and_(
                QueueTicket.department_id == ticket.department_id,
                QueueTicket.status.in_([TicketStatus.WAITING, TicketStatus.CALLED]),
                QueueTicket.queue_position < ticket.queue_position
            )
        )
    )
    people_ahead_count = people_ahead.scalar()
    
    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        customer_name=ticket.customer_name,
        customer_phone=ticket.customer_phone,
        customer_email=ticket.customer_email,
        service_id=ticket.service_id,
        service_name=service.name,
        department_id=ticket.department_id,
        department_name=department.name,
        status=ticket.status,
        priority=ticket.priority,
        queue_position=ticket.queue_position,
        form_data=ticket.form_data or {},
        notes=ticket.notes,
        estimated_wait_time=people_ahead_count * service.estimated_duration if service.estimated_duration else 5,
        created_at=ticket.created_at,
        called_at=ticket.called_at,
        served_at=ticket.served_at,
        completed_at=ticket.completed_at
    )

@router.get("/department/{department_id}/queue", response_model=List[TicketResponse])
async def get_department_queue(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get tickets in queue for department
    result = await db.execute(
        select(QueueTicket, Service, Department)
        .join(Service)
        .join(Department)
        .where(
            and_(
                QueueTicket.department_id == department_id,
                QueueTicket.status.in_([
                    TicketStatus.WAITING, 
                    TicketStatus.CALLED, 
                    TicketStatus.SERVING
                ])
            )
        )
        .order_by(QueueTicket.queue_position.asc())
    )
    
    tickets = []
    for ticket, service, department in result:
        tickets.append(TicketResponse(
            id=ticket.id,
            ticket_number=ticket.ticket_number,
            customer_name=ticket.customer_name,
            customer_phone=ticket.customer_phone,
            customer_email=ticket.customer_email,
            service_id=ticket.service_id,
            service_name=service.name,
            department_id=ticket.department_id,
            department_name=department.name,
            status=ticket.status,
            priority=ticket.priority,
            queue_position=ticket.queue_position,
            form_data=ticket.form_data,
            notes=ticket.notes,
            estimated_wait_time=ticket.estimated_wait_time,
            created_at=ticket.created_at,
            called_at=ticket.called_at,
            served_at=ticket.served_at,
            completed_at=ticket.completed_at
        ))
    
    return tickets

@router.put("/{ticket_id}/call", response_model=TicketResponse)
async def call_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get ticket
    result = await db.execute(
        select(QueueTicket, Service, Department)
        .join(Service)
        .join(Department)
        .where(QueueTicket.id == ticket_id)
    )
    ticket_info = result.first()
    
    if not ticket_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ticket, service, department = ticket_info
    
    # Update ticket status
    ticket.status = TicketStatus.CALLED
    ticket.called_at = datetime.utcnow()
    ticket.staff_id = current_user.id
    
    await db.commit()
    await db.refresh(ticket)
    
    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        customer_name=ticket.customer_name,
        customer_phone=ticket.customer_phone,
        customer_email=ticket.customer_email,
        service_id=ticket.service_id,
        service_name=service.name,
        department_id=ticket.department_id,
        department_name=department.name,
        status=ticket.status,
        priority=ticket.priority,
        queue_position=ticket.queue_position,
        form_data=ticket.form_data,
        notes=ticket.notes,
        estimated_wait_time=ticket.estimated_wait_time,
        created_at=ticket.created_at,
        called_at=ticket.called_at,
        served_at=ticket.served_at,
        completed_at=ticket.completed_at
    )

@router.put("/{ticket_id}/serve", response_model=TicketResponse)
async def serve_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get ticket
    result = await db.execute(
        select(QueueTicket, Service, Department)
        .join(Service)
        .join(Department)
        .where(QueueTicket.id == ticket_id)
    )
    ticket_info = result.first()
    
    if not ticket_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ticket, service, department = ticket_info
    
    # Update ticket status
    ticket.status = TicketStatus.SERVING
    ticket.served_at = datetime.utcnow()
    ticket.staff_id = current_user.id
    
    await db.commit()
    await db.refresh(ticket)
    
    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        customer_name=ticket.customer_name,
        customer_phone=ticket.customer_phone,
        customer_email=ticket.customer_email,
        service_id=ticket.service_id,
        service_name=service.name,
        department_id=ticket.department_id,
        department_name=department.name,
        status=ticket.status,
        priority=ticket.priority,
        queue_position=ticket.queue_position,
        form_data=ticket.form_data,
        notes=ticket.notes,
        estimated_wait_time=ticket.estimated_wait_time,
        created_at=ticket.created_at,
        called_at=ticket.called_at,
        served_at=ticket.served_at,
        completed_at=ticket.completed_at
    )

@router.put("/{ticket_id}/complete", response_model=TicketResponse)
async def complete_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get ticket
    result = await db.execute(
        select(QueueTicket, Service, Department)
        .join(Service)
        .join(Department)
        .where(QueueTicket.id == ticket_id)
    )
    ticket_info = result.first()
    
    if not ticket_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    ticket, service, department = ticket_info
    
    # Update ticket
    ticket.status = TicketStatus.COMPLETED
    ticket.completed_at = datetime.utcnow()
    ticket.staff_id = current_user.id
    
    if ticket_update.notes:
        ticket.notes = ticket_update.notes
    
    await db.commit()
    await db.refresh(ticket)
    
    return TicketResponse(
        id=ticket.id,
        ticket_number=ticket.ticket_number,
        customer_name=ticket.customer_name,
        customer_phone=ticket.customer_phone,
        customer_email=ticket.customer_email,
        service_id=ticket.service_id,
        service_name=service.name,
        department_id=ticket.department_id,
        department_name=department.name,
        status=ticket.status,
        priority=ticket.priority,
        queue_position=ticket.queue_position,
        form_data=ticket.form_data,
        notes=ticket.notes,
        estimated_wait_time=ticket.estimated_wait_time,
        created_at=ticket.created_at,
        called_at=ticket.called_at,
        served_at=ticket.served_at,
        completed_at=ticket.completed_at
    )

@router.get("/next/{department_id}")
async def get_next_ticket(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get next ticket in queue - FIFO order
    result = db.execute(
        select(QueueTicket)
        .where(
            and_(
                QueueTicket.department_id == department_id,
                QueueTicket.status == TicketStatus.WAITING
            )
        )
        .order_by(QueueTicket.queue_position.asc())
        .limit(1)
    )
    
    next_ticket = result.scalar_one_or_none()
    
    if not next_ticket:
        return {"message": "No tickets in queue"}
    
    return {
        "ticket_id": next_ticket.id,
        "ticket_number": next_ticket.ticket_number,
        "customer_name": next_ticket.customer_name,
        "form_data": next_ticket.form_data
    }

# Staff Call Action - Core functionality for Staff Dashboard
@router.put("/{ticket_id}/call", response_model=TicketResponse)
async def call_next_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
    # TODO: Add back authentication after testing
    # current_user: User = Depends(get_current_user)
):
    """Staff calls the next customer - updates status from waiting to called"""
    try:
        # Get ticket with service and department info
        result = db.execute(
            select(QueueTicket, Service, Department)
            .join(Service)
            .join(Department)
            .where(QueueTicket.id == ticket_id)
        )
        ticket_info = result.first()
        
        if not ticket_info:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )
        
        ticket, service, department = ticket_info
        
        # Verify ticket is in waiting status
        if ticket.status != TicketStatus.WAITING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot call ticket with status: {ticket.status}"
            )
        
        # Update ticket status: waiting → called
        ticket.status = TicketStatus.CALLED
        ticket.called_at = datetime.utcnow()
        # TODO: Use current_user.id after re-enabling auth
        # ticket.staff_id = current_user.id
        
        db.commit()
        db.refresh(ticket)
        
        # TODO: Send WebSocket notification to customer
        # This will be implemented in Step 3
        
        return TicketResponse(
            id=ticket.id,
            ticket_number=ticket.ticket_number,
            customer_name=ticket.customer_name,
            customer_phone=ticket.customer_phone or "",
            customer_email=ticket.customer_email,
            service_id=ticket.service_id,
            service_name=service.name,
            department_id=ticket.department_id,
            department_name=department.name,
            status=ticket.status,
            priority=ticket.priority,
            queue_position=ticket.queue_position,
            form_data=ticket.form_data or {},
            notes=ticket.notes,
            estimated_wait_time=ticket.estimated_wait_time,
            created_at=ticket.created_at,
            called_at=ticket.called_at,
            served_at=ticket.served_at,
            completed_at=ticket.completed_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling ticket: {str(e)}")

# Simple test endpoint without authentication
@router.put("/test/{ticket_id}/call")
async def test_call_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Test endpoint for Staff call action without auth"""
    try:
        # Get ticket
        result = db.execute(
            select(QueueTicket)
            .where(QueueTicket.id == ticket_id)
        )
        ticket = result.scalar_one_or_none()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Update ticket status: waiting → called
        ticket.status = TicketStatus.CALLED
        ticket.called_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        
        # Send WebSocket notification to Customer waiting on /waiting page
        # Note: WebSocket manager instance needs to be passed from main.py
        # For now, we'll add this as a TODO and implement in main integration
        
        return {
            "success": True,
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "old_status": "waiting",
            "new_status": ticket.status,
            "called_at": ticket.called_at,
            "message": f"Successfully called ticket {ticket.ticket_number}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Get next ticket for Staff to call (FIFO order)
@router.get("/next-to-call/{department_id}")
async def get_next_ticket_to_call(
    department_id: int,
    db: Session = Depends(get_db)
):
    """Get next waiting ticket in FIFO order for Staff to call"""
    try:
        # Get next ticket in queue - FIFO order (oldest waiting ticket first)
        result = db.execute(
            select(QueueTicket)
            .where(
                and_(
                    QueueTicket.department_id == department_id,
                    QueueTicket.status == TicketStatus.WAITING
                )
            )
            .order_by(QueueTicket.queue_position.asc(), QueueTicket.created_at.asc())
            .limit(1)
        )
        
        next_ticket = result.scalar_one_or_none()
        
        if not next_ticket:
            return {
                "success": False,
                "message": "No tickets waiting in queue",
                "ticket": None
            }
        
        return {
            "success": True,
            "message": f"Next ticket to call: {next_ticket.ticket_number}",
            "ticket": {
                "id": next_ticket.id,
                "ticket_number": next_ticket.ticket_number,
                "customer_name": next_ticket.customer_name,
                "queue_position": next_ticket.queue_position,
                "created_at": next_ticket.created_at,
                "form_data": next_ticket.form_data or {}
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting next ticket: {str(e)}")

# Test endpoint for Staff Dashboard queue without authentication
@router.get("/test/department/{department_id}/queue")
async def test_get_department_queue(
    department_id: int,
    db: Session = Depends(get_db)
):
    """Test endpoint to get department queue without auth for Staff Dashboard"""
    try:
        # Get tickets in queue for department (exclude completed tickets)
        result = db.execute(
            select(QueueTicket, Service, Department)
            .select_from(QueueTicket)
            .join(Service, QueueTicket.service_id == Service.id)
            .join(Department, Service.department_id == Department.id)
            .where(
                and_(
                    QueueTicket.department_id == department_id,
                    QueueTicket.status.in_([
                        TicketStatus.WAITING, 
                        TicketStatus.CALLED, 
                        TicketStatus.SERVING
                    ])
                )
            )
            .order_by(QueueTicket.queue_position.asc())
        )
        
        tickets = []
        for ticket, service, department in result:
            tickets.append({
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "customer_name": ticket.customer_name,
                "customer_phone": ticket.customer_phone,
                "service_name": service.name,
                "department_name": department.name,
                "status": ticket.status,
                "queue_position": ticket.queue_position,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "called_at": ticket.called_at.isoformat() if ticket.called_at else None,
                "estimated_wait_time": ticket.estimated_wait_time
            })
        
        return {
            "success": True,
            "count": len(tickets),
            "tickets": tickets
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting department queue: {str(e)}")

# Get ticket status for Customer waiting page
@router.get("/status/{ticket_id}")
def get_ticket_status_for_customer(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get ticket status for Customer waiting page - no auth required"""
    try:
        # Get ticket first
        ticket_result = db.execute(
            select(QueueTicket).where(QueueTicket.id == ticket_id)
        )
        ticket = ticket_result.scalar_one_or_none()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Get service info
        service_result = db.execute(
            select(Service).where(Service.id == ticket.service_id)
        )
        service = service_result.scalar_one_or_none()
        
        # Get department info
        department_result = db.execute(
            select(Department).where(Department.id == ticket.department_id)
        )
        department = department_result.scalar_one_or_none()
        
        # Get current serving ticket in same department
        current_serving_result = db.execute(
            select(QueueTicket.ticket_number)
            .where(
                and_(
                    QueueTicket.department_id == ticket.department_id,
                    QueueTicket.status == TicketStatus.SERVING
                )
            )
            .limit(1)
        )
        current_serving = current_serving_result.scalar()
        
        # Count people ahead in queue (tickets with lower queue_position that are still waiting/called)
        people_ahead = db.execute(
            select(func.count(QueueTicket.id))
            .where(
                and_(
                    QueueTicket.department_id == ticket.department_id,
                    QueueTicket.status.in_([TicketStatus.WAITING, TicketStatus.CALLED]),
                    QueueTicket.queue_position < ticket.queue_position
                )
            )
        ).scalar() or 0
        
        return {
            "success": True,
            "ticket": {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "customer_name": ticket.customer_name,
                "status": ticket.status,
                "queue_position": ticket.queue_position,
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "called_at": ticket.called_at.isoformat() if ticket.called_at else None
            },
            "queue_info": {
                "people_ahead": people_ahead,
                "current_serving": current_serving,
                "estimated_wait_time": people_ahead * 5,  # 5 minutes per person
                "department_name": department.name,
                "service_name": service.name
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ticket status: {str(e)}")

# Simple test endpoint for Customer waiting page
@router.get("/simple-status/{ticket_id}")
def get_simple_ticket_status(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Simple ticket status for Customer waiting page"""
    try:
        # Get ticket only
        ticket = db.execute(
            select(QueueTicket).where(QueueTicket.id == ticket_id)
        ).scalar_one_or_none()
        
        if not ticket:
            return {"success": False, "message": "Ticket not found"}
        
        # Count people ahead
        people_ahead = db.execute(
            select(func.count(QueueTicket.id))
            .where(
                and_(
                    QueueTicket.department_id == ticket.department_id,
                    QueueTicket.status == TicketStatus.WAITING,
                    QueueTicket.queue_position < ticket.queue_position
                )
            )
        ).scalar() or 0
        
        return {
            "success": True,
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_name": ticket.customer_name,
            "status": ticket.status,
            "queue_position": ticket.queue_position,
            "people_ahead": people_ahead,
            "estimated_wait": people_ahead * 5,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "called_at": ticket.called_at.isoformat() if ticket.called_at else None
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Simple services endpoint for Service Registration page
@router.get("/services-list")
def get_services_for_registration(db: Session = Depends(get_db)):
    """Get all services for Service Registration page - no auth required"""
    try:
        # Get all services with department info
        result = db.execute(
            select(Service, Department)
            .select_from(Service)
            .join(Department, Service.department_id == Department.id)
            .where(Service.is_active == True)
            .order_by(Department.id, Service.name)
        )
        
        services = []
        for service, department in result:
            services.append({
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "department_id": service.department_id,
                "department_name": department.name,
                "estimated_duration": service.estimated_duration,
                "code": service.code
            })
        
        return {
            "success": True,
            "count": len(services),
            "services": services
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# Feedback endpoints
@router.post("/feedback")
def submit_feedback(
    feedback_data: dict,
    db: Session = Depends(get_db)
):
    """Submit customer feedback for a ticket"""
    try:
        from ...models.feedback import Feedback
        from sqlalchemy import select
        
        # Validate ticket exists
        ticket = db.execute(
            select(Ticket).where(Ticket.id == feedback_data.get("ticket_id"))
        ).scalar_one_or_none()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Create feedback
        feedback = Feedback(
            ticket_id=feedback_data.get("ticket_id"),
            overall_rating=feedback_data.get("overall_rating"),
            service_rating=feedback_data.get("service_rating"),
            staff_rating=feedback_data.get("staff_rating"),
            wait_time_rating=feedback_data.get("wait_time_rating"),
            additional_comments=feedback_data.get("additional_comments"),
            is_anonymous=feedback_data.get("is_anonymous", False)
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.id
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}


@router.post("/complaints")
def submit_complaint(
    complaint_data: dict,
    db: Session = Depends(get_db)
):
    """Submit customer complaint for a ticket"""
    try:
        from ...models.complaint import Complaint
        from sqlalchemy import select
        
        # Validate ticket exists
        ticket = db.execute(
            select(Ticket).where(Ticket.id == complaint_data.get("ticket_id"))
        ).scalar_one_or_none()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Create complaint
        complaint = Complaint(
            ticket_id=complaint_data.get("ticket_id"),
            description=complaint_data.get("description"),
            severity=complaint_data.get("severity", "minor"),
            status="pending",
            is_anonymous=complaint_data.get("is_anonymous", False)
        )
        
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        
        return {
            "success": True,
            "message": "Complaint submitted successfully",
            "complaint_id": complaint.id
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}


@router.get("/{ticket_id}/feedback")
def get_ticket_feedback(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get feedback for a specific ticket"""
    try:
        from ...models.feedback import Feedback
        from sqlalchemy import select
        
        feedback = db.execute(
            select(Feedback).where(Feedback.ticket_id == ticket_id)
        ).scalars().all()
        
        feedback_list = []
        for f in feedback:
            feedback_list.append({
                "id": f.id,
                "overall_rating": f.overall_rating,
                "service_rating": f.service_rating,
                "staff_rating": f.staff_rating,
                "wait_time_rating": f.wait_time_rating,
                "additional_comments": f.additional_comments,
                "created_at": f.created_at.isoformat() if f.created_at else None
            })
        
        return {
            "success": True,
            "feedback": feedback_list
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{ticket_id}/complaints")
def get_ticket_complaints(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Get complaints for a specific ticket"""
    try:
        from ...models.complaint import Complaint
        from sqlalchemy import select
        
        complaints = db.execute(
            select(Complaint).where(Complaint.ticket_id == ticket_id)
        ).scalars().all()
        
        complaint_list = []
        for c in complaints:
            complaint_list.append({
                "id": c.id,
                "description": c.description,
                "severity": c.severity,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
                "resolution_notes": c.resolution_notes
            })
        
        return {
            "success": True,
            "complaints": complaint_list
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
