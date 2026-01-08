# FastAPI Backend Router - Staff APIs

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, desc, func, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from ....core.database import get_db
from ....core.security import get_current_user_sync
from ....models import User, QueueTicket, Department, Service, TicketStatus

router = APIRouter()

@router.get("/queue")
def get_staff_queue(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get tickets in queue for staff's department"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Get tickets that can be called (waiting or called)
    tickets = db.query(
        QueueTicket.id,
        QueueTicket.ticket_number,
        QueueTicket.customer_name,
        QueueTicket.customer_phone,
        QueueTicket.status,
        QueueTicket.created_at,
        QueueTicket.called_at,
        Service.name.label('service_name')
    ).join(Service, QueueTicket.service_id == Service.id).filter(
        and_(
            QueueTicket.department_id == current_user.department_id,
            QueueTicket.status.in_(['waiting', 'called'])
        )
    ).order_by(QueueTicket.created_at).all()
    
    return [
        {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_name": ticket.customer_name,
            "customer_phone": ticket.customer_phone,
            "service_name": ticket.service_name,
            "status": ticket.status,
            "created_at": ticket.created_at.isoformat(),
            "called_at": ticket.called_at.isoformat() if ticket.called_at else None,
            "wait_time": int((datetime.now() - ticket.created_at).total_seconds() / 60)
        }
        for ticket in tickets
    ]

@router.post("/queue/call-next")
def call_next_ticket(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Call the next waiting ticket - only if no tickets are currently in 'called' status"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Check if staff already has a called ticket
    current_ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.staff_id == current_user.id,
            QueueTicket.status == 'called'
        )
    ).first()
    
    if current_ticket:
        raise HTTPException(status_code=400, detail="Please complete serving current ticket before calling next")
    
    # Find next waiting ticket only
    next_ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.department_id == current_user.department_id,
            QueueTicket.status == 'waiting'
        )
    ).order_by(QueueTicket.queue_position).first()
    
    if not next_ticket:
        raise HTTPException(status_code=404, detail="No waiting tickets in queue")
    
    # Update ticket status to called
    next_ticket.status = 'called'
    next_ticket.called_at = datetime.now()
    next_ticket.staff_id = current_user.id
    
    db.commit()
    db.refresh(next_ticket)
    
    return {
        "id": next_ticket.id,
        "ticket_number": next_ticket.ticket_number,
        "customer_name": next_ticket.customer_name,
        "service_name": next_ticket.service.name if next_ticket.service else None,
        "status": next_ticket.status
    }

@router.put("/tickets/{ticket_id}/complete")
def complete_ticket(  # Đổi từ async thành sync
    ticket_id: int,
    completion_data: dict = None,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Complete a ticket - only allowed when ticket is in 'called' status"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")

    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            QueueTicket.status == 'called',
            QueueTicket.department_id == current_user.department_id
        )
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or is not in 'called' status")

    # Update ticket status to completed
    ticket.status = 'completed'
    ticket.completed_at = datetime.now()

    # Set staff and served time
    ticket.staff_id = current_user.id
    ticket.served_at = datetime.now()
    if not ticket.called_at:
        ticket.called_at = datetime.now()

    # Add notes if provided
    if completion_data and completion_data.get('notes'):
        ticket.notes = completion_data['notes']

    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket completed successfully",
        "ticket_id": ticket.id,
        "redirect_to_review": f"/review/{ticket.id}"
    }

@router.put("/tickets/{ticket_id}/call")
def call_specific_ticket(  # Đổi từ async thành sync
    ticket_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Call a specific ticket"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            QueueTicket.status.in_(['waiting', 'called']),
            QueueTicket.department_id == current_user.department_id
        )
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or cannot be called")
    
    # Update ticket to called status if it was waiting
    if ticket.status == 'waiting':
        ticket.status = 'called'
        ticket.called_at = datetime.now()
    
    ticket.staff_id = current_user.id
    
    db.commit()
    db.refresh(ticket)
    
    return {"message": "Ticket called", "ticket_id": ticket.id, "status": ticket.status}


@router.put("/tickets/{ticket_id}/cancel")
def cancel_ticket(  # Đổi từ async thành sync function
    ticket_id: int,
    cancel_data: dict = None,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Cancel a ticket - set status to 'cancelled'"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")

    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            QueueTicket.department_id == current_user.department_id,
            QueueTicket.status.in_(['waiting', 'called'])
        )
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or cannot be cancelled")

    ticket.status = 'no_show'  # Use valid enum value instead of 'cancelled'
    ticket.cancelled_at = datetime.now()
    if cancel_data and cancel_data.get('notes'):
        ticket.notes = cancel_data.get('notes')

    db.commit()
    db.refresh(ticket)

    return {"message": "Ticket cancelled successfully", "ticket_id": ticket.id}

@router.put("/tickets/{ticket_id}/review")
async def submit_ticket_review(
    ticket_id: int,
    review_data: dict,
    db: Session = Depends(get_db)
):
    """Submit customer review for completed ticket"""
    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            QueueTicket.status == 'completed'
        )
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or not completed")
    
    # Update ticket with review data
    ticket.service_rating = review_data.get('service_rating')
    ticket.staff_rating = review_data.get('staff_rating') 
    ticket.speed_rating = review_data.get('speed_rating')
    ticket.overall_rating = review_data.get('overall_rating')
    ticket.review_comments = review_data.get('comments', '')
    ticket.reviewed_at = datetime.now()
    
    db.commit()
    
    return {
        "message": "Review submitted successfully", 
        "ticket_id": ticket.id,
        "overall_rating": ticket.overall_rating
    }

@router.get("/current-ticket")
def get_current_ticket(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff's current ticket being served"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    current_ticket = db.query(QueueTicket).join(Service).filter(
        and_(
            QueueTicket.staff_id == current_user.id,
            QueueTicket.status == 'called'
        )
    ).first()
    
    if not current_ticket:
        return None
    
    service = db.query(Service).filter(Service.id == current_ticket.service_id).first()
    
    return {
        "id": current_ticket.id,
        "ticket_number": current_ticket.ticket_number,
        "customer_name": current_ticket.customer_name,
        "customer_phone": current_ticket.customer_phone,
        "service_name": service.name if service else "Unknown",
        "status": current_ticket.status,
        "created_at": current_ticket.created_at.isoformat() if current_ticket.created_at else None,
        "called_at": current_ticket.called_at.isoformat() if current_ticket.called_at else None
    }

@router.post("/queue/complete/{ticket_id}")
def complete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Complete a ticket service"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Get the ticket
    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            QueueTicket.staff_id == current_user.id,
            QueueTicket.status == 'called'
        )
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or not assigned to you")
    
    # Update ticket status to completed
    ticket.status = 'completed'
    ticket.completed_at = datetime.now()
    
    db.commit()
    
    return {"message": "Ticket completed successfully", "ticket_id": ticket_id}

@router.post("/queue/cancel/{ticket_id}")
def cancel_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Cancel a ticket (no show)"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    # Get the ticket
    ticket = db.query(QueueTicket).filter(
        and_(
            QueueTicket.id == ticket_id,
            or_(
                QueueTicket.staff_id == current_user.id,
                QueueTicket.department_id == current_user.department_id
            )
        )
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Update ticket status to cancelled (no_show)
    ticket.status = 'cancelled'
    ticket.cancelled_at = datetime.now()
    
    # If it was called ticket, clear staff assignment
    if ticket.status == 'called':
        ticket.staff_id = None
    
    db.commit()
    
    return {"message": "Ticket cancelled successfully", "ticket_id": ticket_id}
    ticket = db.query(QueueTicket).filter(QueueTicket.id == ticket_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {
        "ticket_id": ticket.id,
        "status": ticket.status,
        "can_review": ticket.status == 'completed' and not ticket.reviewed_at,
        "already_reviewed": ticket.reviewed_at is not None,
        "customer_name": ticket.customer_name
    }

@router.get("/dashboard/overview")
def get_dashboard_overview(  # Đổi từ async thành sync
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get dashboard overview for staff with new performance metrics"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    try:
        print(f"🔍 Loading dashboard for staff ID: {current_user.id} ({current_user.full_name})")
        
        # 1. Vé đã phục vụ hôm nay (status = completed) - Fix: dùng completed_at
        tickets_served_query = db.execute(text("""
            SELECT COUNT(*) as count
            FROM queue_tickets 
            WHERE staff_id = :staff_id 
            AND status = 'completed'
            AND DATE(COALESCE(completed_at, created_at)) = CURRENT_DATE
        """), {"staff_id": current_user.id})
        tickets_served = tickets_served_query.fetchone()[0] or 0
        
        # 2. Khiếu nại liên quan đến staff (check ticket_id có liên kết với staff)
        complaints_query = db.execute(text("""
            SELECT COUNT(*) as count
            FROM ticket_complaints tc
            INNER JOIN queue_tickets qt ON tc.ticket_id = qt.id
            WHERE qt.staff_id = :staff_id
            AND DATE(tc.created_at) = CURRENT_DATE
        """), {"staff_id": current_user.id})
        complaints = complaints_query.fetchone()[0] or 0
        
        # 3. Đánh giá TB (giống logic ở Quản lý hàng đợi)
        rating_query = db.execute(text("""
            SELECT COALESCE(AVG(overall_rating), 0) as avg_rating
            FROM queue_tickets 
            WHERE staff_id = :staff_id 
            AND overall_rating IS NOT NULL
            AND overall_rating > 0
        """), {"staff_id": current_user.id})
        avg_rating = rating_query.fetchone()[0] or 0.0
        avg_rating = round(float(avg_rating), 1) if avg_rating else 0.0
        
        # 4. Xếp hạng staff theo thuật toán: Đánh giá TB → Khiếu nại (ít hơn)
        ranking_query = db.execute(text("""
            WITH staff_stats AS (
                SELECT 
                    u.id,
                    u.full_name,
                    COALESCE(AVG(qt.overall_rating), 0) as avg_rating,
                    COUNT(DISTINCT tc.id) as complaint_count
                FROM users u
                LEFT JOIN queue_tickets qt ON u.id = qt.staff_id AND qt.overall_rating IS NOT NULL
                LEFT JOIN ticket_complaints tc ON tc.ticket_id = qt.id
                WHERE u.role = 'staff' AND u.department_id = :dept_id
                GROUP BY u.id, u.full_name
            ),
            ranked_staff AS (
                SELECT 
                    id, full_name, avg_rating, complaint_count,
                    ROW_NUMBER() OVER (
                        ORDER BY avg_rating DESC, complaint_count ASC, id
                    ) as rank
                FROM staff_stats
            )
            SELECT 
                COUNT(*) as total_staff,
                (SELECT rank FROM ranked_staff WHERE id = :staff_id) as current_rank
            FROM ranked_staff
        """), {"staff_id": current_user.id, "dept_id": current_user.department_id})
        
        ranking_result = ranking_query.fetchone()
        total_staff = ranking_result[0] or 1
        current_rank = ranking_result[1] or 1
        
        print(f"📊 Stats for staff {current_user.id}: tickets={tickets_served}, complaints={complaints}, rating={avg_rating:.1f}, rank={current_rank}/{total_staff}")
        
        # Return compatible format với frontend expectations
        return {
            # Format mới cho tab Hiệu suất
            "todayStats": {
                "ticketsServed": tickets_served,
                "complaints": complaints,
                "avgRating": round(avg_rating, 1)
            },
            "rankingPosition": current_rank,
            "totalStaff": total_staff,
            "weeklyStats": [],  # Placeholder for charts
            
            # Format cũ để tương thích với tab Quản lý hàng đợi
            "completed_today": tickets_served,
            "average_rating": round(avg_rating, 1),
            "success": True
        }
        
    except Exception as e:
        print(f"Error in staff dashboard overview: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error loading dashboard data: {str(e)}"
        )

@router.post("/status/online")
def set_staff_online(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Set staff as online when they access dashboard"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    try:
        # Update online status only (last_login column doesn't exist)
        db.execute(text("""
            UPDATE users 
            SET is_active = true 
            WHERE id = :user_id
        """), {"user_id": current_user.id})
        db.commit()
        
        print(f"👤 Staff {current_user.full_name} ({current_user.id}) is now ONLINE")
        return {"status": "online", "user_id": current_user.id}
        
    except Exception as e:
        print(f"Error setting staff online: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating online status: {str(e)}")

@router.post("/status/offline")  
def set_staff_offline(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Set staff as offline"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    try:
        # Offline status doesn't need database update (last_login column doesn't exist)
        # Could add is_active = false if needed
        db.commit()
        
        print(f"👤 Staff {current_user.full_name} ({current_user.id}) is now OFFLINE")
        return {"status": "offline", "user_id": current_user.id}
        
    except Exception as e:
        print(f"Error setting staff offline: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating offline status: {str(e)}")

@router.get("/notifications")
def get_staff_notifications(
    limit: int = 10,
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff notifications - TEMPORARILY DISABLED"""
    if current_user.role not in ["staff", "manager", "admin"]:
        raise HTTPException(status_code=403, detail="Staff access required")
    
    try:
        # TODO: NOTIFICATIONS FEATURE - ĐANG TẠM NGƯNG PHÁT TRIỂN
        # CHỈ ĐƯỢC PHÁT TRIỂN KHI CÓ LỆNH RÕ RÀNG TỪ USER
        
        # TEMPORARILY RETURN EMPTY ARRAY TO PREVENT UI ERRORS
        return []
        
        # ORIGINAL CODE - COMMENTED OUT:
        # notifications = db.query(StaffNotification).filter(
        #     StaffNotification.recipient_id == current_user.id
        # ).order_by(desc(StaffNotification.created_at)).limit(limit).all()
        
        # return [{
        #     "id": notif.id,
        #     "title": notif.title,
        #     "message": notif.message,
        #     "type": notif.notification_type,  # Fix: dùng notification_type thay vì type
        #     "read": notif.is_read,  # Fix: dùng is_read thay vì read
        #     "created_at": notif.created_at.isoformat() if notif.created_at else None
        # } for notif in notifications]
        
    except Exception as e:
        print(f"Error getting staff notifications: {str(e)}")
        return []  # Return empty array instead of error to not break UI

@router.post("/complaints")
async def submit_complaint(
    complaint_data: dict,
    db: Session = Depends(get_db)
):
    """Submit customer complaint"""
    try:
        # Insert complaint into database
        result = db.execute(text("""
            INSERT INTO complaints (
                ticket_id, complaint_text, category, severity, status, created_at
            ) VALUES (
                :ticket_id, :complaint_text, :category, :severity, 'open', NOW()
            ) RETURNING id
        """), {
            "ticket_id": complaint_data.get('ticket_id'),
            "complaint_text": complaint_data.get('description', complaint_data.get('complaint_text')),
            "category": complaint_data.get('category', 'service_quality'),
            "severity": complaint_data.get('severity', 'medium')
        })
        
        db.commit()
        complaint_id = result.fetchone()[0]
        
        return {
            "message": "Complaint submitted successfully",
            "complaint_id": complaint_id
        }
        
    except Exception as error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting complaint: {str(error)}")

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
                    QueueTicket.status == 'completed',
                    func.date(QueueTicket.served_at) == today
                )
            ).count()
            
            avg_service_time = 0
            avg_rating = 0
            rating_count = 0
        
        # Current serving ticket
        current_serving = db.query(QueueTicket).filter(
            and_(
                QueueTicket.staff_id == current_user.id,
                QueueTicket.status == 'serving'
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

@router.get("/performance/weekly")
def get_staff_weekly_performance(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff performance data for the last 7 days with real database queries"""
    try:
        # 1. TỔNG SỐ VÉ ĐÃ PHỤC VỤ (status = completed)
        total_tickets_query = db.execute(text("""
            SELECT COUNT(*) as count
            FROM queue_tickets 
            WHERE staff_id = :staff_id 
            AND status = 'completed'
        """), {"staff_id": current_user.id})
        total_tickets = total_tickets_query.fetchone()[0] or 0
        
        # 2. TỔNG SỐ KHIẾU NẠI (assigned_to staff trong ticket_complaints)
        total_complaints_query = db.execute(text("""
            SELECT COUNT(*) as count
            FROM ticket_complaints tc
            INNER JOIN queue_tickets qt ON tc.ticket_id = qt.id
            WHERE qt.staff_id = :staff_id
        """), {"staff_id": current_user.id})
        total_complaints = total_complaints_query.fetchone()[0] or 0
        
        # 3. ĐÁNH GIÁ TRUNG BÌNH THỰC (overall_rating từ queue_tickets - CHUẨN HÓA)
        avg_rating_query = db.execute(text("""
            SELECT COALESCE(AVG(overall_rating), 0) as avg_rating
            FROM queue_tickets 
            WHERE staff_id = :staff_id 
            AND overall_rating IS NOT NULL
            AND overall_rating > 0
        """), {"staff_id": current_user.id})
        avg_rating = avg_rating_query.fetchone()[0] or 0.0
        avg_rating = round(float(avg_rating), 1) if avg_rating else 0.0
        
        # 4. DỮ LIỆU 7 NGÀY QUA CHO BIỂU ĐỒ (thực từ database)
        weekly_data_query = db.execute(text("""
            SELECT 
                DATE(COALESCE(qt.completed_at, qt.created_at)) as service_date,
                COUNT(CASE WHEN qt.status = 'completed' THEN 1 END) as tickets_count,
                COUNT(DISTINCT tc.id) as complaints_count
            FROM queue_tickets qt
            LEFT JOIN ticket_complaints tc ON tc.ticket_id = qt.id
            WHERE qt.staff_id = :staff_id 
            AND DATE(COALESCE(qt.completed_at, qt.created_at)) >= CURRENT_DATE - 6
            GROUP BY DATE(COALESCE(qt.completed_at, qt.created_at))
            ORDER BY service_date DESC
        """), {"staff_id": current_user.id})
        
        weekly_results = weekly_data_query.fetchall()
        
        # 5. XẾP HẠNG STAFF THEO DEPARTMENT
        ranking_query = db.execute(text("""
            WITH staff_ratings AS (
                SELECT 
                    u.id,
                    u.full_name,
                    COALESCE(AVG(qt.overall_rating), 0) as avg_rating,
                    COUNT(DISTINCT tc.id) as complaint_count
                FROM users u
                LEFT JOIN queue_tickets qt ON u.id = qt.staff_id AND qt.overall_rating IS NOT NULL
                LEFT JOIN ticket_complaints tc ON tc.ticket_id = qt.id
                WHERE u.role = 'staff' AND u.department_id = :dept_id
                GROUP BY u.id, u.full_name
            ),
            ranked_staff AS (
                SELECT 
                    id, avg_rating, complaint_count,
                    ROW_NUMBER() OVER (ORDER BY avg_rating DESC, complaint_count ASC) as rank
                FROM staff_ratings
            )
            SELECT rank FROM ranked_staff WHERE id = :staff_id
        """), {"staff_id": current_user.id, "dept_id": current_user.department_id})
        
        ranking_result = ranking_query.fetchone()
        staff_rank = ranking_result[0] if ranking_result else 1
        
        # Format dữ liệu 7 ngày cho biểu đồ
        chart_data = []
        day_names = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
        
        for i in range(7):
            # Tìm data cho ngày này
            target_date = None
            tickets = 0
            complaints = 0
            
            for row in weekly_results:
                if row[0] and (datetime.now().date() - row[0]).days == i:
                    tickets = row[1] or 0
                    complaints = row[2] or 0
                    break
            
            chart_data.append({
                "day": day_names[6-i],  # Reverse để hiển thị từ T2->CN
                "tickets": tickets,
                "complaints": complaints
            })
        
        return {
            "totalStats": {
                "ticketsServed": total_tickets,
                "complaints": total_complaints, 
                "avgRating": avg_rating
            },
            "ranking": staff_rank,
            "weeklyChart": chart_data,
            "success": True
        }
        
    except Exception as e:
        print(f"Error getting staff weekly performance: {e}")
        return {"error": "Internal server error", "success": False}

@router.get("/performance/ratings-distribution")
def get_staff_ratings_distribution(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get staff ratings distribution (1-5 stars) from actual database"""
    try:
        # Query rating distribution for staff (sử dụng overall_rating - CHUẨN HÓA)
        rating_dist_query = db.execute(text("""
            SELECT 
                overall_rating as rating,
                COUNT(*) as count
            FROM queue_tickets 
            WHERE staff_id = :staff_id 
            AND overall_rating IS NOT NULL 
            AND overall_rating > 0
            GROUP BY overall_rating
            ORDER BY overall_rating DESC
        """), {"staff_id": current_user.id})
        
        rating_results = rating_dist_query.fetchall()
        
        # Initialize all ratings 1-5 with count 0
        rating_distribution = []
        colors = ['bg-gray-400', 'bg-red-400', 'bg-orange-400', 'bg-yellow-400', 'bg-green-400']
        
        for stars in range(5, 0, -1):  # 5 to 1
            count = 0
            for row in rating_results:
                if row[0] == stars:
                    count = row[1]
                    break
            
            rating_distribution.append({
                "stars": stars,
                "count": count,
                "color": colors[stars-1]
            })
        
        return {"ratingDistribution": rating_distribution}
        
    except Exception as e:
        print(f"Error getting ratings distribution: {e}")
        return {"ratingDistribution": []}

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
    
    return {"message": "Ticket cancelled successfully"}

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


@router.get("/department")
def get_staff_department(
    current_user: User = Depends(get_current_user_sync),
    db: Session = Depends(get_db)
):
    """Get current staff's department information"""
    try:
        if not current_user.department_id:
            return {"error": "Staff has no assigned department"}
        
        # Get department info from database
        department = db.query(Department).filter(
            Department.id == current_user.department_id
        ).first()
        
        if not department:
            return {"error": "Department not found"}
        
        return {
            "id": department.id,
            "name": department.name,
            "description": department.description,
            "code": department.code,
            "is_active": department.is_active
        }
        
    except Exception as e:
        print(f"Error getting staff department: {e}")
        return {"error": "Internal server error"}


