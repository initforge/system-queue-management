"""
API Router v1 - Main router for version 1 of the API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.security import get_current_user, require_active_user
from ...models import User
from ...models.service import Service
from ...schemas.auth import UserLogin, Token
from ...schemas.department import DepartmentResponse, DepartmentWithServices
from ...schemas.service import ServiceResponse
from ...schemas.ticket import TicketCreate, TicketResponse
from ...services import (
    authenticate_user, 
    create_access_token,
    get_departments,
    get_department,
    create_ticket,
    get_ticket
)

# Import routers
# from .services import router as services_router
# from .tickets import router as tickets_router
from .roles.staff import router as staff_router
from .feedback import router as feedback_router
from .roles.manager import router as manager_router
from .schedule import router as schedule_router
from .ai_helper import router as ai_helper_router
from .auth import router as auth_router


# Create main API v1 router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(staff_router, prefix="/staff", tags=["Staff"])
api_router.include_router(feedback_router)  # No prefix since it already has /feedback
api_router.include_router(manager_router, prefix="/manager", tags=["Manager"])
api_router.include_router(schedule_router, prefix="/schedule", tags=["Schedule"])
api_router.include_router(ai_helper_router, prefix="/ai-helper", tags=["AI Helper"])
# api_router.include_router(services_router, prefix="/services", tags=["Services"])
# api_router.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])



# Department endpoints
@api_router.get("/departments", response_model=List[DepartmentResponse])
def list_departments(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    departments = get_departments(db, skip, limit, include_inactive)
    return departments

@api_router.get("/departments/{department_id}", response_model=DepartmentWithServices)
def get_department_details(department_id: int, db: Session = Depends(get_db)):
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

# Ticket endpoints
@api_router.post("/tickets/register")
async def register_ticket(
    request: Request,
    db: Session = Depends(get_db)
):
    """Simple ticket registration endpoint"""
    try:
        # Parse JSON body manually
        body = await request.json()
        print(f"Received ticket data: {body}")  # Debug log
        
        # Create ticket directly without complex services
        from ...models.ticket import QueueTicket, TicketStatus
        from datetime import datetime
        
        # Extract required fields
        customer_name = body.get("customer_name")
        service_id = body.get("service_id") 
        department_id = body.get("department_id")
        
        if not all([customer_name, service_id, department_id]):
            raise HTTPException(status_code=400, detail="Missing required fields: customer_name, service_id, department_id")
        
        # Generate department-based ticket number (bank counter style)
        # Get department name for prefix mapping
        from ...models.department import Department
        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Department prefix mapping - Bank style A,B,C,D based on department ID
        dept_prefixes = {
            1: "A",  # Phòng Kế hoạch Tổng hợp
            2: "B",  # Phòng Tài chính Kế toán  
            3: "C",  # Phòng Hành chính Quản trị
            4: "D",  # Phòng Công nghệ Thông tin
        }
        
        # Get prefix based on department ID
        dept_prefix = dept_prefixes.get(department_id, "X")  # X as fallback
        
        # Generate ticket number with uniqueness check
        # Get highest number from all tickets across all departments 
        from sqlalchemy import func, text
        
        # Find the highest number from any ticket (across all time, not just today)
        highest_query = text("""
            SELECT MAX(CAST(SUBSTRING(ticket_number FROM 2) AS INTEGER)) as max_num
            FROM queue_tickets 
            WHERE ticket_number ~ '^[A-Z][0-9]{3}$'
        """)
        result = db.execute(highest_query)
        max_counter = result.scalar() or 0
        
        # Generate unique ticket number with safety check
        counter = max_counter + 1
        max_attempts = 50  # Prevent infinite loop
        
        for attempt in range(max_attempts):
            ticket_number = f"{dept_prefix}{counter:03d}"
            
            # Check if this ticket number already exists
            existing_check = text("SELECT 1 FROM queue_tickets WHERE ticket_number = :ticket_number")
            existing = db.execute(existing_check, {'ticket_number': ticket_number}).scalar()
            
            if not existing:
                break  # Found unique number
                
            counter += 1  # Try next number
            
        else:
            raise HTTPException(status_code=500, detail="Could not generate unique ticket number")
        
        # Auto-assign staff based on workload (least busy staff in the department)
        staff_assignment_query = text("""
            SELECT u.id, u.full_name,
                   COUNT(qt.id) as current_workload
            FROM users u
            LEFT JOIN queue_tickets qt ON u.id = qt.staff_id 
                AND qt.status IN ('waiting', 'called')
            WHERE u.department_id = :dept_id 
                AND u.role = 'staff' 
                AND u.is_active = true
            GROUP BY u.id, u.full_name
            ORDER BY current_workload ASC, u.id ASC
            LIMIT 1
        """)
        
        staff_result = db.execute(staff_assignment_query, {'dept_id': department_id})
        assigned_staff = staff_result.fetchone()
        
        assigned_staff_id = assigned_staff.id if assigned_staff else None
        
        # Create ticket using raw SQL to avoid enum issues
        from sqlalchemy import text
        
        insert_query = text("""
            INSERT INTO queue_tickets 
            (ticket_number, customer_name, customer_phone, customer_email, 
             service_id, department_id, staff_id, notes, estimated_wait_time, status, created_at)
            VALUES 
            (:ticket_number, :customer_name, :customer_phone, :customer_email,
             :service_id, :department_id, :staff_id, :notes, :estimated_wait_time, 'waiting', NOW())
            RETURNING id, ticket_number, customer_name, status, created_at
        """)
        
        result = db.execute(insert_query, {
            'ticket_number': ticket_number,
            'customer_name': customer_name,
            'customer_phone': body.get("customer_phone"),
            'customer_email': body.get("customer_email"),
            'service_id': service_id,
            'department_id': department_id,
            'staff_id': assigned_staff_id,
            'notes': body.get("notes"),
            'estimated_wait_time': 30
        })
        
        ticket_row = result.fetchone()
        db.commit()
        
        return {
            "success": True,
            "ticket": {
                "id": ticket_row.id,
                "ticket_number": ticket_row.ticket_number,
                "customer_name": ticket_row.customer_name,
                "status": ticket_row.status,
                "created_at": ticket_row.created_at.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating ticket: {str(e)}")

@api_router.post("/tickets")
def create_new_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db)
):
    try:
        print(f"📝 API Router: Creating ticket - service_id={ticket_data.service_id}, dept={ticket_data.department_id}")
        
        ticket = create_ticket(
            db=db,
            service_id=ticket_data.service_id,
            customer_name=ticket_data.customer_name,
            customer_phone=ticket_data.customer_phone,
            customer_email=getattr(ticket_data, 'customer_email', None),
            department_id=ticket_data.department_id,
            notes=getattr(ticket_data, 'notes', None)
        )
        
        print(f"✅ API Router: Ticket created successfully - ID: {ticket.id}")
        
        # Return simple dict to avoid serialization issues
        return {
            "success": True,
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_name": ticket.customer_name,
            "status": ticket.status,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None
        }
    except ValueError as e:
        print(f"❌ API Router ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"💥 API Router Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/tickets/{ticket_id}/status")
def get_ticket_status_public(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Public endpoint for customers to check ticket status"""
    try:
        from ...models.ticket import QueueTicket
        
        ticket = db.query(QueueTicket).filter(QueueTicket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        # Calculate people ahead (waiting tickets created before this ticket)
        people_ahead = 0
        estimated_wait = 0
        
        if ticket.status == "waiting":
            people_ahead = db.query(QueueTicket).filter(
                QueueTicket.department_id == ticket.department_id,
                QueueTicket.status == "waiting",
                QueueTicket.created_at < ticket.created_at
            ).count()
            
            # Get service estimated time for wait calculation
            from ...models.service import Service
            service = db.query(Service).filter(Service.id == ticket.service_id).first()
            service_time = service.estimated_duration if service else 15  # default 15 min
            
            estimated_wait = people_ahead * service_time
        
        return {
            "success": True,
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_name": ticket.customer_name,
            "status": ticket.status,
            "queue_position": people_ahead + 1 if ticket.status == "waiting" else 0,
            "people_ahead": people_ahead,
            "estimated_wait": estimated_wait,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "called_at": ticket.called_at.isoformat() if ticket.called_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ticket: {str(e)}")

@api_router.post("/tickets/{ticket_id}/cancel")
def cancel_ticket_public(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Public endpoint for customers to cancel their ticket"""
    try:
        from ...models.ticket import QueueTicket
        
        ticket = db.query(QueueTicket).filter(QueueTicket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        if ticket.status != "waiting":
            raise HTTPException(status_code=400, detail="Only waiting tickets can be cancelled")
        
        # Update ticket status to no_show
        ticket.status = "no_show"
        ticket.completed_at = datetime.now()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Ticket cancelled successfully",
            "ticket_id": ticket.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cancelling ticket: {str(e)}")

@api_router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket_details(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user)
):
    ticket = get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

# Health check endpoint
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# Services endpoint - Working version with department filtering
@api_router.get("/services")
def list_services(department_id: int = None, db: Session = Depends(get_db)):
    """Get all services, optionally filtered by department"""
    try:
        # Use raw SQL since ORM has issues
        from sqlalchemy import text
        
        if department_id:
            # Filter by department
            result = db.execute(text("""
                SELECT id, name, description, department_id, estimated_duration, is_active 
                FROM services 
                WHERE department_id = :dept_id AND is_active = true
                ORDER BY id
            """), {"dept_id": department_id}).fetchall()
        else:
            # Get all services
            result = db.execute(text("""
                SELECT id, name, description, department_id, estimated_duration, is_active 
                FROM services 
                WHERE is_active = true
                ORDER BY department_id, id
            """)).fetchall()
        
        services_list = []
        for row in result:
            services_list.append({
                "id": row[0],
                "name": row[1], 
                "description": row[2],
                "department_id": row[3],
                "estimated_duration": row[4],
                "is_active": row[5]
            })
        
        print(f"Returning {len(services_list)} services")
        
        # Return format expected by frontend
        return {
            "success": True,
            "services": services_list
        }
        
    except Exception as e:
        print(f"Services API Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "services": []
        }