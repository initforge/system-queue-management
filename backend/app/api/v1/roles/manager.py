"""
Manager API Routes
Handles manager-specific operations for staff management and schedule oversight
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, text
from typing import List, Optional
from datetime import date, datetime, timezone

from ....core.database import get_db
from ....core.security import get_current_user, get_current_user_sync
from ....models import User, QueueTicket, Service, TicketComplaint, Department, StaffNotification
from ....services.schedule_service import ScheduleService

router = APIRouter()

@router.get("/dashboard-stats")
async def get_manager_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics for managers"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can access this endpoint"
        )
    
    try:
        # service = ScheduleService(db)  # Commented out - schedule models not available
        
        # Get department staff count
        staff_count = db.query(User).filter(
            User.department_id == current_user.department_id,
            User.role == 'staff',
            User.is_active == True
        ).count()
        
        # Get pending leave requests
        # pending_leaves = service.get_leave_requests(status_filter='pending')
        pending_leaves = []  # Temporary
        
        # Get pending check-ins
        # pending_checkins = service.get_checkins(status_filter='pending')
        pending_checkins = []  # Temporary
        
        # Get today's scheduled staff
        # today_scheduled = service.get_weekly_schedule(date.today().isoformat())
        today_scheduled = []  # Temporary
        
        return {
            "staff_count": staff_count,
            "pending_leave_requests": len(pending_leaves),
            "pending_checkins": len(pending_checkins), 
            "today_scheduled_staff": len(today_scheduled.get('schedules', [])),
            "department_id": current_user.department_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving manager stats: {str(e)}"
        )

@router.get("/department-staff")
async def get_department_staff(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all staff members in manager's department"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can access this endpoint"
        )
    
    try:
        staff_members = db.query(User).filter(
            User.department_id == current_user.department_id,
            User.role == 'staff',
            User.is_active == True
        ).all()
        
        return [{
            "id": staff.id,
            "full_name": staff.full_name,
            "email": staff.email,
            "phone": staff.phone,
            "username": staff.username
        } for staff in staff_members]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving department staff: {str(e)}"
        )

@router.get("/pending-approvals")
async def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending approvals for manager"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can access this endpoint"
        )
    
    try:
        # service = ScheduleService(db)  # Commented out - schedule models not available
        
        # Get pending leave requests
        # pending_leaves = service.get_leave_requests(status_filter='pending')
        pending_leaves = []  # Temporary
        
        # Get pending check-ins
        # pending_checkins = service.get_checkins(status_filter='pending')
        pending_checkins = []  # Temporary
        
        # Get pending shift exchanges
        pending_exchanges = service.get_shift_exchanges(status_filter='pending')
        
        return {
            "leave_requests": pending_leaves,
            "checkin_requests": pending_checkins,
            "shift_exchanges": pending_exchanges,
            "total_pending": len(pending_leaves) + len(pending_checkins) + len(pending_exchanges)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving pending approvals: {str(e)}"
        )


@router.get("/complaints")
async def get_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all complaints for manager's department"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can access this endpoint"
        )
    
    try:
        # Get ticket complaints from manager's department
        complaints = db.query(TicketComplaint).join(
            QueueTicket, TicketComplaint.ticket_id == QueueTicket.id
        ).filter(
            QueueTicket.department_id == current_user.department_id
        ).order_by(desc(TicketComplaint.created_at)).all()
        
        result = []
        for complaint in complaints:
            complaint_data = {
                "id": complaint.id,
                "customer_name": complaint.customer_name,
                "customer_phone": complaint.customer_phone,
                "customer_email": complaint.customer_email,
                "content": complaint.complaint_text,
                "status": complaint.status,
                "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                "assigned_to": complaint.assigned_to,
                "staff_name": None,
                "ticket_number": None,
                "rating": complaint.rating
            }
            
            # Get staff name if assigned
            if complaint.assigned_to:
                staff = db.query(User).filter(User.id == complaint.assigned_to).first()
                if staff:
                    complaint_data["staff_name"] = staff.full_name
            
            # Get ticket info
            ticket = db.query(QueueTicket).filter(QueueTicket.id == complaint.ticket_id).first()
            if ticket:
                complaint_data["ticket_number"] = ticket.ticket_number
                # Get staff who served the ticket
                if ticket.staff_id:
                    serving_staff = db.query(User).filter(User.id == ticket.staff_id).first()
                    if serving_staff:
                        complaint_data["staff_name"] = serving_staff.full_name
            
            result.append(complaint_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving complaints: {str(e)}"
        )


@router.post("/complaints/{complaint_id}/assign")
async def assign_complaint(
    complaint_id: int,
    assignment_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign complaint to staff member"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can assign complaints"
        )
    
    try:
        complaint = db.query(TicketComplaint).filter(TicketComplaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        staff_id = assignment_data.get("staff_id")
        if staff_id:
            # Verify staff exists and is in same department
            staff = db.query(User).filter(
                and_(
                    User.id == staff_id,
                    User.department_id == current_user.department_id,
                    User.role == 'staff'
                )
            ).first()
            
            if not staff:
                raise HTTPException(status_code=404, detail="Staff member not found in your department")
            
            complaint.assigned_to = staff_id
            complaint.status = "waiting"
        else:
            complaint.assigned_to = None
            complaint.status = "waiting"
        
        complaint.updated_at = datetime.now(timezone.utc)
        db.commit()
        
        return {"message": "Complaint assignment updated successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning complaint: {str(e)}"
        )


@router.get("/staff")
async def get_staff_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all staff in manager's department with current status"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can access this endpoint"
        )
    
    try:
        staff_members = db.query(User).filter(
            and_(
                User.department_id == current_user.department_id,
                User.role == 'staff',
                User.is_active == True
            )
        ).all()
        
        result = []
        for staff in staff_members:
            # Get current ticket count
            current_tickets = db.query(QueueTicket).filter(
                and_(
                    QueueTicket.staff_id == staff.id,
                    QueueTicket.status == 'called'
                )
            ).count()
            
            # Determine status
            status = "busy" if current_tickets > 0 else "online"
            
            result.append({
                "id": staff.id,
                "full_name": staff.full_name,
                "username": staff.username,
                "email": staff.email,
                "phone": staff.phone,
                "counter": f"Quầy {staff.counter_id}" if staff.counter_id else "Chưa gán",
                "status": status,
                "performance": 4.0,  # Default performance score
                "current_tickets": current_tickets
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving staff list: {str(e)}"
        )

@router.get("/manager-info")
def get_manager_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_sync)
):
    """Get manager information and dashboard data"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can access this endpoint"
        )
    
    try:
        # For manager.01@qstream.vn (ID=2) - manages ALL complaints from all staff
        # For future managers - only manage complaints assigned to them
        
        if current_user.id == 2:  # manager.01@qstream.vn - universal manager
            # Get ALL complaints across all staff
            waiting_complaints = db.query(TicketComplaint).filter(
                TicketComplaint.status == 'waiting'
            ).count()
            
            completed_complaints = db.query(TicketComplaint).filter(
                TicketComplaint.status == 'completed'
            ).count()
            
            # Get recent complaints from ALL staff with full details
            recent_complaints_query = db.query(
                TicketComplaint,
                User.full_name.label('staff_name'),
                User.email.label('staff_email'),
                QueueTicket.ticket_number,
                QueueTicket.customer_phone.label('customer_phone'),
                Service.name.label('service_name'),
                Department.name.label('department_name')
            ).outerjoin(
                QueueTicket, TicketComplaint.ticket_id == QueueTicket.id
            ).outerjoin(
                User, QueueTicket.staff_id == User.id  # FIX: JOIN với staff_id thay vì assigned_to
            ).outerjoin(
                Service, QueueTicket.service_id == Service.id
            ).outerjoin(
                Department, QueueTicket.department_id == Department.id
            ).order_by(desc(TicketComplaint.created_at)).limit(10)
            
            recent_complaints = recent_complaints_query.all()
        else:
            # Future managers - only get complaints assigned to them
            waiting_complaints = db.query(TicketComplaint).filter(
                and_(
                    TicketComplaint.assigned_to == current_user.id,
                    TicketComplaint.status == 'waiting'
                )
            ).count()
            
            completed_complaints = db.query(TicketComplaint).filter(
                and_(
                    TicketComplaint.assigned_to == current_user.id,
                    TicketComplaint.status == 'completed'
                )
            ).count()
            
            # Get recent complaints assigned to this manager
            recent_complaints_query = db.query(
                TicketComplaint,
                User.full_name.label('staff_name'),
                User.email.label('staff_email'),
                QueueTicket.ticket_number,
                QueueTicket.customer_phone.label('customer_phone'),
                Service.name.label('service_name'),
                Department.name.label('department_name')
            ).outerjoin(
                QueueTicket, TicketComplaint.ticket_id == QueueTicket.id
            ).outerjoin(
                User, QueueTicket.staff_id == User.id
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
            customer_phone = row.customer_phone  # Labeled field from QueueTicket
            service_name = row.service_name  # Labeled field
            department_name = row.department_name  # Labeled field
            
            complaints_data.append({
                "id": complaint.id,
                "ticket_id": complaint.ticket_id,
                "ticket_number": ticket_number,
                "customer_name": complaint.customer_name,
                "customer_phone": customer_phone or complaint.customer_phone,  # Use QueueTicket phone first, fallback to complaint
                "customer_email": complaint.customer_email,
                "subject": complaint.complaint_text[:50] + "..." if len(complaint.complaint_text) > 50 else complaint.complaint_text,  # Use complaint_text as subject
                "content": complaint.complaint_text,  # Map complaint_text to content for UI compatibility
                "complaint_text": complaint.complaint_text,
                "category": "service",  # Default category since TicketComplaint doesn't have category
                "status": complaint.status,
                "staff_name": staff_name,
                "staff_email": staff_email,
                "service_name": service_name,
                "department_name": department_name,
                "priority": "medium",  # Default priority since we removed severity
                "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
                "resolved_at": complaint.resolved_at.isoformat() if complaint.resolved_at else None
            })
        
        # Thêm dashboard stats tổng hợp cho Manager Dashboard với queries chính xác
        dashboard_stats_query = db.execute(text("""
            SELECT 
                -- 1. Nhân viên online (dựa trên last_login trong 30 phút gần đây để thực tế hơn)
                (SELECT COUNT(*) FROM users 
                 WHERE role = 'staff' 
                 AND is_active = true 
                 AND last_login > NOW() - INTERVAL '30 minutes') as online_staff,
                
                -- 2. Yêu cầu đang xử lý (tất cả tickets waiting của mọi nhân viên)
                (SELECT COUNT(*) FROM queue_tickets WHERE status = 'waiting') as active_tickets,
                
                -- 3. Hiệu suất TB (tất cả ratings của mọi tickets)
                (SELECT COALESCE(AVG(overall_rating), 0) FROM queue_tickets 
                 WHERE overall_rating IS NOT NULL AND overall_rating > 0) as avg_performance
        """))
        
        dashboard_result = dashboard_stats_query.fetchone()
        online_staff = dashboard_result[0] or 0
        active_tickets = dashboard_result[1] or 0
        average_performance = round(float(dashboard_result[2] or 0), 1)
        
        print(f"🔍 Manager Dashboard Stats: online_staff={online_staff}, active_tickets={active_tickets}, avg_performance={average_performance}")
        
        return {
            "manager_name": current_user.full_name or current_user.username,
            "waiting_complaints": waiting_complaints,
            "completed_complaints": completed_complaints,
            "recent_complaints": complaints_data,
            # Dashboard stats tổng hợp
            "dashboard_stats": {
                "online_staff": online_staff,
                "active_tickets": active_tickets,
                "average_performance": average_performance
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving manager info: {str(e)}"
        )

@router.post("/complaints/{complaint_id}/resolve")
@router.put("/complaints/{complaint_id}/resolve")  # Support both POST and PUT
async def resolve_complaint(
    complaint_id: int,
    response_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve a ticket complaint"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can resolve complaints"
        )
    
    print(f"🔍 DEBUG: Resolving complaint {complaint_id} by user {current_user.email} (ID: {current_user.id})")
    print(f"🔍 DEBUG: Response data: {response_data}")
    
    try:
        # For manager.01@qstream.vn (ID=2) - can resolve ALL complaints
        # For future managers - only resolve complaints assigned to them
        if current_user.id == 2:  # Universal manager
            complaint = db.query(TicketComplaint).filter(
                TicketComplaint.id == complaint_id
            ).first()
        else:
            complaint = db.query(TicketComplaint).filter(
                and_(
                    TicketComplaint.id == complaint_id,
                    TicketComplaint.assigned_to == current_user.id
                )
            ).first()
        
        if not complaint:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Complaint not found or not accessible"
            )
        
        # Update complaint status and details
        complaint.status = 'completed'
        complaint.manager_response = response_data.get('response', '')
        complaint.resolved_at = datetime.now(timezone.utc)
        
        # Assign to current manager if not already assigned
        if not complaint.assigned_to:
            complaint.assigned_to = current_user.id
        
        db.commit()
        
        return {"message": "Complaint resolved successfully"}
        
    except Exception as e:
        db.rollback()
        print(f"🚨 DEBUG: Error resolving complaint: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving complaint: {str(e)}"
        )


@router.post("/send-staff-notification")
async def send_staff_notification(
    notification_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send notification to staff member"""
    if current_user.role not in ['manager', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers can send notifications"
        )
    
    try:
        # Find staff member by email
        staff_member = db.query(User).filter(
            User.email == notification_data.get('recipient_email'),
            User.role == 'staff'
        ).first()
        
        if not staff_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff member not found"
            )
        
        # Create notification in database
        complaint_details = {
            "customer_name": notification_data.get('customer_name'),
            "customer_phone": notification_data.get('customer_phone'), 
            "ticket_number": notification_data.get('ticket_number'),
            "content": notification_data.get('complaint_content'),
            "service_name": notification_data.get('service_name'),
            "department_name": notification_data.get('department_name')
        }
        
        new_notification = StaffNotification(
            recipient_id=staff_member.id,
            sender_id=current_user.id,
            title=notification_data.get('title', 'Khiếu nại từ khách hàng'),
            message=notification_data.get('message'),
            notification_type="complaint",
            priority="normal",
            complaint_details=complaint_details
        )
        
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)
        
        # Create response payload for frontend
        notification_payload = {
            "type": "complaint_notification",
            "title": new_notification.title,
            "message": new_notification.message,
            "time": new_notification.created_at.strftime('%H:%M:%S'),
            "recipient_email": notification_data.get('recipient_email'),
            "complaintDetails": complaint_details
        }
        
        return {
            "message": f"Notification sent successfully to {staff_member.full_name}",
            "recipient": staff_member.full_name,
            "notification": notification_payload,
            "notification_id": new_notification.id,
            "sent_at": new_notification.created_at.isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending notification: {str(e)}"
        )