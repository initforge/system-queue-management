# FastAPI Backend Router - Staff APIs

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
# import json
from ...core.database import get_db
from ...core.security import get_current_user_sync
from ...models import User, QueueTicket, Department, Service, TicketStatus, TicketComplaint
# from ...websocket_manager import websocket_manager

router = APIRouter()

@router.get("/department")
def get_staff_department(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff's department information"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Manager doesn't have department_id - they manage all departments
    if current_user.role == "manager":
        return {
            "id": None,
            "name": "Tất cả phòng ban",
            "description": "Quản lý tất cả các phòng ban",
            "is_active": True
        }
    
    # Get department info for staff
    department = db.query(Department).filter(Department.id == current_user.department_id).first()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return {
        "id": department.id,
        "name": department.name,
        "description": department.description,
        "is_active": department.is_active
    }

@router.get("/current-ticket")
def get_current_ticket(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff's current ticket being served"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Find current ticket assigned to this staff with status 'called'
    current_ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.staff_id == current_user.id,
            QueueTicket.status == "called"
        )
    ).first()
    
    if not current_ticket:
        return {"current_ticket": None}
    
    # Get service name
    service = db.query(Service).filter(Service.id == current_ticket.service_id).first()
    
    return {
        "current_ticket": {
            "id": current_ticket.id,
            "ticket_number": current_ticket.ticket_number,
            "customer_name": current_ticket.customer_name,
            "service_name": service.name if service else "Unknown Service",
            "status": current_ticket.status,
            "called_at": current_ticket.called_at.isoformat() if current_ticket.called_at else None
        }
    }

@router.get("/chat/rooms")
def get_chat_rooms(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get chat rooms for staff - placeholder for now"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # For now, return empty array since chat feature not implemented
    return {"chat_rooms": []}

@router.get("/queue")
def get_staff_queue(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get tickets in queue for staff's department"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    print(f"🎫 DEBUG: Current user: {current_user.email}, role: {current_user.role}, dept_id: {current_user.department_id}")
    
    # Get real tickets from database
    # Get tickets with service names via LEFT JOIN to handle missing services
    try:
        tickets = db.query(QueueTicket, Service.name.label('service_name')).outerjoin(
            Service, QueueTicket.service_id == Service.id
        ).filter(
            and_(
                QueueTicket.department_id == current_user.department_id,
                QueueTicket.status == "waiting"
            )
        ).order_by(QueueTicket.created_at).all()
        
        print(f"Found {len(tickets)} waiting tickets for department {current_user.department_id}")
        
        # Format for frontend
        ticket_list = []
        for ticket, service_name in tickets:
            ticket_data = {
                "id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "customer_name": ticket.customer_name,
                "customer_phone": ticket.customer_phone,
                "service_id": ticket.service_id,
                "service_name": service_name or "Unknown Service",
                "status": ticket.status.value if hasattr(ticket.status, 'value') else str(ticket.status),
                "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                "estimated_wait_time": ticket.estimated_wait_time
            }
            ticket_list.append(ticket_data)
            print(f"Ticket: {ticket_data}")
        
        print(f"Returning {len(ticket_list)} tickets to frontend")
        return ticket_list
        
    except Exception as e:
        print(f"Error in staff/queue API: {e}")
        return []

@router.put("/queue/call-next")
def call_next_ticket(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Call the next QueueTicket in queue - only if staff has no current ticket"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Check if staff already has a called ticket (in progress)
    current_ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.staff_id == current_user.id,
            QueueTicket.status == "called"
        )
    ).first()
    
    if current_ticket:
        raise HTTPException(
            status_code=400, 
            detail=f"Bạn đang phục vụ ticket #{current_ticket.ticket_number}. Vui lòng hoàn thành hoặc hủy trước khi gọi ticket mới."
        )
    
    # Find next waiting QueueTicket
    next_ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.department_id == current_user.department_id,
            QueueTicket.status == "waiting"
        )
    ).order_by(QueueTicket.created_at).first()  # Order by creation time, not queue_position
    
    if not next_ticket:
        raise HTTPException(status_code=404, detail="No tickets waiting in queue")
    
    # Update QueueTicket status
    next_ticket.status = TicketStatus.called
    next_ticket.called_at = datetime.now()
    next_ticket.staff_id = current_user.id
    
    db.commit()
    db.refresh(next_ticket)
    
    # Get service name
    service = db.query(Service).filter(Service.id == next_ticket.service_id).first()
    
    return {
        "success": True,
        "ticket": {
            "id": next_ticket.id,
            "ticket_number": next_ticket.ticket_number,
            "customer_name": next_ticket.customer_name,
            "service_name": service.name if service else "Unknown Service",
            "status": next_ticket.status.value,
            "called_at": next_ticket.called_at.isoformat() if next_ticket.called_at else None
        }
    }

@router.put("/tickets/{ticket_id}/complete")
async def complete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Complete a called ticket - only allowed if ticket is assigned to current staff"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            QueueTicket.status == "called",
            QueueTicket.staff_id == current_user.id
        )
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket không tìm thấy hoặc không được assign cho bạn")
    
    # Complete the ticket
    ticket.status = "completed"
    ticket.completed_at = datetime.now()
    
    db.commit()
    db.refresh(ticket)
    
    # TODO: Send WebSocket notification to customer about completion
    # message = {
    #     "type": "ticket_completed", 
    #     "ticket_id": ticket.id,
    #     "ticket_number": ticket.ticket_number,
    #     "status": "completed",
    #     "message": "Dịch vụ đã hoàn thành. Bạn sẽ được chuyển đến trang đánh giá."
    # }
    # await websocket_manager.broadcast_to_queue(
    #     json.dumps(message), 
    #     str(ticket.id)
    # )
    
    return {"message": "Ticket đã được hoàn thành", "ticket_id": ticket.id}

@router.put("/tickets/{ticket_id}/cancel")
async def cancel_ticket_staff(
    ticket_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Cancel a called ticket - only allowed if ticket is assigned to current staff"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            QueueTicket.status == "called",
            QueueTicket.staff_id == current_user.id
        )
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket không tìm thấy hoặc không được assign cho bạn")
    
    # Cancel the ticket  
    ticket.status = "no_show"
    ticket.completed_at = datetime.now()
    
    db.commit()
    db.refresh(ticket)
    
    return {"message": "Ticket đã được hủy", "ticket_id": ticket.id}
    ticket.served_at = datetime.now()
    
    db.commit()
    db.refresh(ticket)
    
    return {"message": "Started serving ticket", "ticket_id": ticket.id}

@router.put("/tickets/{ticket_id}/complete")
async def complete_ticket(
    ticket_id: int,
    completion_data: dict,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Complete a QueueTicket"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            QueueTicket.status == TicketStatus.called,
            QueueTicket.staff_id == current_user.id
        )
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or not assigned to you")
    
    ticket.status = TicketStatus.completed
    ticket.completed_at = datetime.now()
    # Note: completion_notes field might not exist in database
    
    db.commit()
    db.refresh(ticket)
    
    return {"message": "Ticket completed successfully", "ticket_id": ticket.id}

@router.get("/performance")
def get_staff_performance_summary(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff performance summary"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    today = date.today()
    
    # Get today's completed tickets by this staff
    completed_today = db.query(QueueTicket).filter(
        and_(
            QueueTicket.staff_id == current_user.id,
            QueueTicket.status == "completed",
            func.date(QueueTicket.completed_at) == today
        )
    ).count()
    
    # Get average service time
    avg_service_time_query = db.query(
        func.avg(
            func.extract('epoch', QueueTicket.completed_at - QueueTicket.served_at) / 60
        )
    ).filter(
        and_(
            QueueTicket.staff_id == current_user.id,
            QueueTicket.status == "completed",
            func.date(QueueTicket.completed_at) == today,
            QueueTicket.served_at.isnot(None),
            QueueTicket.completed_at.isnot(None)
        )
    ).scalar()
    
    avg_service_time = float(avg_service_time_query) if avg_service_time_query else 0
    
    # Get average rating from queue_tickets.overall_rating
    avg_rating_query = db.query(func.avg(QueueTicket.overall_rating)).filter(
        and_(
            QueueTicket.staff_id == current_user.id,
            QueueTicket.status == "completed",
            func.date(QueueTicket.completed_at) == today,
            QueueTicket.overall_rating.isnot(None)
        )
    ).scalar()
    
    avg_rating = float(avg_rating_query) if avg_rating_query else 0
    
    return {
        "todayStats": {
            "ticketsServed": completed_today,
            "avgServiceTime": round(avg_service_time, 1),
            "avgRating": round(avg_rating, 1)
        },
        "weeklyStats": [],
        "rankingPosition": 1,
        "totalStaff": 4
    }

@router.get("/performance/today")  
def get_staff_performance_today(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff performance metrics for today"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    try:
        today = datetime.now().date()
        
        # Try to get performance from staff_performance table first
        performance_record = db.execute(text("""
            SELECT 
                tickets_served, 
                avg_service_time, 
                avg_rating,
                rating_count
            FROM staff_performance 
            WHERE user_id = :user_id AND date = :today
        """), {"user_id": current_user.id, "today": today}).first()
        
        if performance_record:
            tickets_served = performance_record[0] or 0
            avg_service_time = float(performance_record[1] or 0)
            avg_rating = float(performance_record[2] or 0)  
            rating_count = performance_record[3] or 0
        else:
            # Fallback to real-time calculation
            tickets_served = db.query(QueueTicket).filter(
                and_(
                    QueueTicket.staff_id == current_user.id,
                    QueueTicket.status == TicketStatus.completed,
                    func.date(QueueTicket.completed_at) == today
                )
            ).count()
            
            avg_service_time = 0
            avg_rating = 0
            rating_count = 0
        
        # Current serving ticket
        current_serving = db.query(QueueTicket).filter(
            and_(
                QueueTicket.staff_id == current_user.id,
                QueueTicket.status == TicketStatus.completed
            )
        ).first()
        
        return {
            "tickets_served": tickets_served,
            "avg_service_time": avg_service_time,
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "current_serving": {
                "ticket_number": current_serving.ticket_number,
                "customer_name": current_serving.customer_name,
                "service_name": current_serving.service.name if current_serving and current_serving.service else None
            } if current_serving else None
        }
        
    except Exception as e:
        # Return default values if any error occurs
        return {
            "tickets_served": 0,
            "avg_service_time": 0,
            "avg_rating": 0,
            "rating_count": 0,
            "current_serving": None
        }

@router.get("/performance/history")
async def get_staff_performance_history(
    days: int = Query(default=7, ge=1, le=30),
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff performance history"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Daily performance data
    daily_stats = db.execute(text("""
        SELECT 
            DATE(completed_at) as date,
            COUNT(*) as tickets_served,
            AVG(EXTRACT(EPOCH FROM (completed_at - served_at))/60) as avg_service_time
        FROM queue_tickets 
        WHERE staff_id = :staff_id 
        AND status = 'completed'
        AND completed_at >= :start_date
        GROUP BY DATE(completed_at)
        ORDER BY DATE(completed_at)
    """), {"staff_id": current_user.id, "start_date": start_date}).fetchall()
    
    performance_trend = [
        {
            "date": stat[0].strftime('%Y-%m-%d'),
            "tickets_served": stat[1],
            "avg_service_time": round(stat[2] or 0, 1)
        }
        for stat in daily_stats
    ]
    
    return {
        "period_days": days,
        "performance_trend": performance_trend
    }

@router.get("/queue/{department_id}")
async def get_department_queue(
    department_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get current queue for a specific department"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Verify user has access to this department
    if current_user.role == "staff" and current_user.department_id != department_id:
        raise HTTPException(status_code=403, detail="Access to this department denied")
    
    # Get waiting and serving tickets for the department
    query = db.execute(text("""
        SELECT 
            qt.id,
            qt.ticket_number,
            qt.customer_name,
            qt.customer_phone,
            qt.status,
            qt.queue_position,
            qt.created_at,
            s.name as service_name,
            u.full_name as staff_name
        FROM queue_tickets qt
        LEFT JOIN services s ON qt.service_id = s.id
        LEFT JOIN users u ON qt.staff_id = u.id
        WHERE qt.department_id = :dept_id 
        AND qt.status IN ('waiting', 'called', 'serving')
        ORDER BY 
            CASE 
                WHEN qt.status = 'serving' THEN 1
                WHEN qt.status = 'called' THEN 2
                WHEN qt.status = 'waiting' THEN 3
            END,
            qt.queue_position ASC,
            qt.created_at ASC
    """), {"dept_id": department_id})
    
    tickets = []
    for row in query:
        tickets.append({
            "id": row.id,
            "ticket_number": row.ticket_number,
            "customer_name": row.customer_name,
            "customer_phone": row.customer_phone,
            "status": row.status,
            "queue_position": row.queue_position,
            "service_name": row.service_name,
            "staff_name": row.staff_name,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "wait_time": str(datetime.now() - row.created_at).split('.')[0] if row.created_at else "0:00:00"
        })
    
    return tickets

@router.get("/performance/{staff_id}")
async def get_staff_performance(
    staff_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get performance data for a staff member"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Verify access
    if current_user.role == "staff" and current_user.id != staff_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get today's stats
    today_query = db.execute(text("""
        SELECT 
            COALESCE(sp.tickets_served, 0) as tickets_served,
            COALESCE(sp.avg_service_time, 0) as avg_service_time,
            COALESCE(sp.avg_rating, 0) as avg_rating
        FROM staff_performance sp
        WHERE sp.user_id = :staff_id AND sp.date = CURRENT_DATE
    """), {"staff_id": staff_id})
    
    today_result = today_query.fetchone()
    today_stats = {
        "ticketsServed": today_result.tickets_served if today_result else 0,
        "avgServiceTime": today_result.avg_service_time if today_result else 0,
        "avgRating": float(today_result.avg_rating) if today_result else 0.0
    }
    
    # Get weekly stats (last 7 days)
    weekly_query = db.execute(text("""
        SELECT 
            sp.date,
            sp.tickets_served,
            sp.avg_service_time,
            sp.avg_rating
        FROM staff_performance sp
        WHERE sp.user_id = :staff_id 
        AND sp.date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY sp.date DESC
    """), {"staff_id": staff_id})
    
    weekly_stats = []
    for row in weekly_query:
        weekly_stats.append({
            "date": row.date.isoformat(),
            "ticketsServed": row.tickets_served,
            "avgServiceTime": row.avg_service_time,
            "avgRating": float(row.avg_rating)
        })
    
    # Get ranking among all staff in department
    ranking_query = db.execute(text("""
        WITH staff_rankings AS (
            SELECT 
                u.id,
                u.full_name,
                COALESCE(SUM(sp.tickets_served), 0) as total_tickets,
                ROW_NUMBER() OVER (ORDER BY COALESCE(SUM(sp.tickets_served), 0) DESC) as rank
            FROM users u
            LEFT JOIN staff_performance sp ON u.id = sp.user_id 
                AND sp.date >= CURRENT_DATE - INTERVAL '7 days'
            WHERE u.role = 'staff' 
            AND u.department_id = (SELECT department_id FROM users WHERE id = :staff_id)
            GROUP BY u.id, u.full_name
        )
        SELECT 
            rank,
            (SELECT COUNT(*) FROM staff_rankings) as total_staff
        FROM staff_rankings 
        WHERE id = :staff_id
    """), {"staff_id": staff_id})
    
    ranking_result = ranking_query.fetchone()
    ranking_position = ranking_result.rank if ranking_result else 1
    total_staff = ranking_result.total_staff if ranking_result else 1
    
    return {
        "todayStats": today_stats,
        "weeklyStats": weekly_stats,
        "rankingPosition": ranking_position,
        "totalStaff": total_staff
    }

@router.get("/settings/{staff_id}")
async def get_staff_settings(
    staff_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get settings for a staff member"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    if current_user.role == "staff" and current_user.id != staff_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.execute(text("""
        SELECT theme, language, notifications_enabled, display_mode
        FROM staff_settings 
        WHERE user_id = :staff_id
    """), {"staff_id": staff_id})
    
    result = query.fetchone()
    if result:
        return {
            "theme": result.theme,
            "language": result.language,
            "notifications": result.notifications_enabled,
            "displayMode": result.display_mode
        }
    else:
        # Return default settings
        return {
            "theme": "light",
            "language": "vi", 
            "notifications": True,
            "displayMode": "compact"
        }

@router.post("/call-next")
async def call_next_ticket(
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Call the next QueueTicket in queue for staff member"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    staff_id = request_data.get("staff_id")
    department_id = request_data.get("department_id")
    
    # Verify staff has access
    if current_user.role == "staff" and current_user.id != staff_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if staff is already serving someone
    current_serving = db.execute(text("""
        SELECT id FROM queue_tickets 
        WHERE staff_id = :staff_id AND status = 'serving'
    """), {"staff_id": staff_id}).fetchone()
    
    if current_serving:
        raise HTTPException(status_code=400, detail="Staff is already serving a customer")
    
    # Get next QueueTicket in queue (FIFO - First In, First Out)
    next_ticket_query = db.execute(text("""
        SELECT id, ticket_number, customer_name, customer_phone, service_id
        FROM queue_tickets 
        WHERE department_id = :dept_id 
        AND status = 'waiting' 
        ORDER BY created_at ASC 
        LIMIT 1
    """), {"dept_id": department_id})
    
    next_ticket = next_ticket_query.fetchone()
    if not next_ticket:
        return {"QueueTicket": None, "message": "No customers waiting"}
    
    # Update QueueTicket status to called
    db.execute(text("""
        UPDATE queue_tickets 
        SET status = 'called', 
            staff_id = :staff_id, 
            called_at = NOW()
        WHERE id = :ticket_id
    """), {"staff_id": staff_id, "ticket_id": next_ticket.id})
    
    db.commit()
    
    return {
        "QueueTicket": {
            "id": next_ticket.id,
            "ticket_number": next_ticket.ticket_number,
            "customer_name": next_ticket.customer_name,
            "customer_phone": next_ticket.customer_phone,
            "service_id": next_ticket.service_id
        }
    }

@router.post("/complete-QueueTicket/{ticket_id}")
async def complete_ticket(
    ticket_id: int,
    request_data: Dict[str, Any],
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Mark a QueueTicket as completed"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    staff_id = request_data.get("staff_id")
    
    # Verify staff has access
    if current_user.role == "staff" and current_user.id != staff_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update QueueTicket status
    db.execute(text("""
        UPDATE queue_tickets 
        SET status = 'completed',
            completed_at = NOW()
        WHERE id = :ticket_id AND staff_id = :staff_id
    """), {"ticket_id": ticket_id, "staff_id": staff_id})
    
    db.commit()
    
    # Update staff performance for today
    db.execute(text("""
        INSERT INTO staff_performance (user_id, department_id, date, tickets_served)
        VALUES (:staff_id, (SELECT department_id FROM users WHERE id = :staff_id), CURRENT_DATE, 1)
        ON CONFLICT (user_id, date) 
        DO UPDATE SET tickets_served = staff_performance.tickets_served + 1
    """), {"staff_id": staff_id})
    
    db.commit()
    
    return {"message": "QueueTicket completed successfully"}


@router.put("/queue/cancel/{ticket_id}")
def cancel_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Cancel a ticket in queue"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    try:
        # Find the ticket
        ticket = db.query(QueueTicket).filter(
            and_(
                QueueTicket.id == ticket_id,
                QueueTicket.department_id == current_user.department_id,
                QueueTicket.status.in_([TicketStatus.waiting, TicketStatus.called, TicketStatus.completed])
            )
        ).first()
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found or cannot be cancelled")
        
        # Update ticket status
        ticket.status = TicketStatus.no_show
        ticket.staff_id = current_user.id
        ticket.completed_at = datetime.now()
        
        db.commit()
        db.refresh(ticket)
        
        return {
            "success": True,
            "message": "Ticket cancelled successfully",
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

@router.get("/dashboard/overview")
def get_dashboard_overview(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get overview stats for staff dashboard"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    today = date.today()
    
    # Manager sees all departments, staff sees only their department
    if current_user.role == "manager":
        # Get queue count across all departments
        queue_count = db.query(QueueTicket).filter(
            QueueTicket.status == "waiting"
        ).count()
        
        # Manager doesn't have completed tickets (they don't serve customers)
        completed_today = 0
        
        # Get current tickets being served by any staff
        current_serving = db.query(QueueTicket).filter(
            QueueTicket.status == "called"
        ).first()
        
        # Average rating across all departments from queue_tickets.overall_rating
        avg_rating_result = db.query(func.avg(QueueTicket.overall_rating)).filter(
            and_(
                QueueTicket.status == "completed",
                QueueTicket.overall_rating.isnot(None)
            )
        ).scalar()
        
    else:
        # Staff logic - same as before
        # Get queue count in staff's department
        queue_count = db.query(QueueTicket).filter(
            and_(
                QueueTicket.department_id == current_user.department_id,
                QueueTicket.status == "waiting"
            )
        ).count()
        
        # Get today's completed tickets by this staff
        completed_today = db.query(QueueTicket).filter(
            and_(
                QueueTicket.staff_id == current_user.id,
                QueueTicket.status == "completed",
                func.date(QueueTicket.completed_at) == today
            )
        ).count()
        
        # Get current serving ticket for this staff
        current_serving = db.query(QueueTicket).filter(
            and_(
                QueueTicket.staff_id == current_user.id,
                QueueTicket.status == "called"
            )
        ).first()
        
        # Get average rating for this staff from tickets
        avg_rating_result = db.query(func.avg(QueueTicket.overall_rating)).filter(
            and_(
                QueueTicket.staff_id == current_user.id,  # Only ratings for this staff
                QueueTicket.status == "completed",
                QueueTicket.overall_rating.isnot(None)
            )
        ).scalar()
    
    # Calculate average rating
    try:
        average_rating = float(avg_rating_result) if avg_rating_result else 0.0
    except Exception as e:
        print(f"Rating query error: {e}")
        average_rating = 0.0
    
    return {
        "queue_count": queue_count,
        "completed_today": completed_today,
        "average_rating": round(average_rating, 1),
        "current_serving": {
            "id": current_serving.id,
            "ticket_number": current_serving.ticket_number,
            "customer_name": current_serving.customer_name
        } if current_serving else None
    }

@router.post("/tickets/{ticket_id}/review")
@router.put("/tickets/{ticket_id}/review")  # Add PUT method support
def submit_ticket_review(
    ticket_id: int,
    review_data: dict,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Submit review/rating for a completed ticket"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Get the ticket
    ticket = db.query(QueueTicket).filter(QueueTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket with ratings and review
    if 'service_rating' in review_data:
        ticket.service_rating = review_data['service_rating']
    if 'staff_rating' in review_data:
        ticket.staff_rating = review_data['staff_rating']
    if 'speed_rating' in review_data:
        ticket.speed_rating = review_data['speed_rating']
    if 'overall_rating' in review_data:
        ticket.overall_rating = review_data['overall_rating']
    if 'review_comments' in review_data:
        ticket.review_comments = review_data['review_comments']
    
    ticket.reviewed_at = datetime.utcnow()
    
    # Auto-create complaint for low ratings (1-2 stars) or negative feedback
    should_create_complaint = False
    complaint_reason = []
    
    if review_data.get('overall_rating') and review_data['overall_rating'] <= 2:
        should_create_complaint = True
        complaint_reason.append(f"Overall rating: {review_data['overall_rating']}/5 stars")
    
    if review_data.get('staff_rating') and review_data['staff_rating'] <= 2:
        should_create_complaint = True
        complaint_reason.append(f"Staff rating: {review_data['staff_rating']}/5 stars")
    
    if review_data.get('service_rating') and review_data['service_rating'] <= 2:
        should_create_complaint = True
        complaint_reason.append(f"Service rating: {review_data['service_rating']}/5 stars")
    
    # Create complaint if conditions met
    complaint_id = None
    if should_create_complaint:
        complaint = TicketComplaint(
            ticket_id=ticket.id,
            customer_name=ticket.customer_name or "Anonymous Customer",
            customer_email=ticket.customer_email,
            customer_phone=ticket.customer_phone,
            complaint_text=f"Customer gave low ratings: {', '.join(complaint_reason)}. Comments: {review_data.get('review_comments', 'No additional comments')}",
            status="waiting",
            assigned_to=ticket.staff_id,  # Assign to the staff who served the ticket
            rating=review_data.get('overall_rating')
        )
        
        db.add(complaint)
        db.flush()  # Get the complaint ID
        complaint_id = complaint.id
    
    try:
        db.commit()
        db.refresh(ticket)
        
        response = {
            "success": True,
            "message": "Review submitted successfully",
            "ticket_id": ticket_id
        }
        
        if complaint_id:
            response["complaint_created"] = True
            response["complaint_id"] = complaint_id
            response["message"] = "Review submitted and complaint created due to low rating"
        
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting review: {str(e)}")


@router.get("/notifications")
def get_staff_notifications(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get notifications for the current staff member"""
    try:
        # Build query
        query = db.query(StaffNotification).filter(
            StaffNotification.recipient_id == current_user.id,
            StaffNotification.is_archived == False
        )
        
        if unread_only:
            query = query.filter(StaffNotification.is_read == False)
        
        # Get total count
        total_count = query.count()
        
        # Get unread count 
        unread_count = db.query(StaffNotification).filter(
            StaffNotification.recipient_id == current_user.id,
            StaffNotification.is_read == False,
            StaffNotification.is_archived == False
        ).count()
        
        # Get notifications with pagination
        notifications = query.order_by(desc(StaffNotification.created_at))\
                            .offset(offset)\
                            .limit(limit)\
                            .all()
        
        # Format notifications for frontend
        formatted_notifications = []
        for notification in notifications:
            formatted_notification = {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "priority": notification.priority,
                "complaint_details": notification.complaint_details,
                "is_read": notification.is_read,
                "is_archived": notification.is_archived,
                "created_at": notification.created_at.isoformat(),
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "time": notification.created_at.strftime('%H:%M:%S')
            }
            formatted_notifications.append(formatted_notification)
        
        return {
            "notifications": formatted_notifications,
            "total_count": total_count,
            "unread_count": unread_count,
            "current_page": offset // limit + 1 if limit > 0 else 1,
            "total_pages": (total_count + limit - 1) // limit if limit > 0 else 1
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")


@router.patch("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    try:
        notification = db.query(StaffNotification).filter(
            StaffNotification.id == notification_id,
            StaffNotification.recipient_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        db.commit()
        db.refresh(notification)
        
        return {
            "success": True,
            "message": "Notification marked as read",
            "notification_id": notification_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating notification: {str(e)}")


@router.patch("/notifications/mark-all-read") 
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for the current staff member"""
    try:
        db.query(StaffNotification).filter(
            StaffNotification.recipient_id == current_user.id,
            StaffNotification.is_read == False
        ).update({
            StaffNotification.is_read: True,
            StaffNotification.read_at: datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "All notifications marked as read"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating notifications: {str(e)}")


@router.delete("/notifications/{notification_id}")
def archive_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Archive (soft delete) a notification"""
    try:
        notification = db.query(StaffNotification).filter(
            StaffNotification.id == notification_id,
            StaffNotification.recipient_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_archived = True
        notification.archived_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Notification archived",
            "notification_id": notification_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error archiving notification: {str(e)}")