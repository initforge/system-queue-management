"""
AI Functions Service
Contains functions that AI can call to query real data from the system
"""
from datetime import date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

from app.models.ticket import QueueTicket, TicketStatus
from app.models.schedule import StaffSchedule, Shift
from app.models.user import User

logger = logging.getLogger(__name__)


class AIFunctions:
    """Service containing all functions available for AI to call"""
    
    def __init__(self, db: Session, user_id: int, user_role: str, department_id: int = None):
        self.db = db
        self.user_id = user_id
        self.user_role = user_role
        self.department_id = department_id
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status for today"""
        try:
            today = date.today()
            
            # Base query
            query = self.db.query(QueueTicket).filter(
                func.date(QueueTicket.created_at) == today
            )
            
            # Staff only sees their own tickets, manager sees department
            if self.user_role == 'staff':
                query = query.filter(QueueTicket.staff_id == self.user_id)
            elif self.department_id:
                # Manager sees department tickets
                staff_ids = self.db.query(User.id).filter(
                    User.department_id == self.department_id
                ).all()
                staff_id_list = [s[0] for s in staff_ids]
                query = query.filter(QueueTicket.staff_id.in_(staff_id_list))
            
            waiting = query.filter(QueueTicket.status == TicketStatus.waiting).count()
            serving = query.filter(QueueTicket.status == TicketStatus.serving).count()
            completed = query.filter(QueueTicket.status == TicketStatus.completed).count()
            
            return {
                "success": True,
                "data": {
                    "today": today.isoformat(),
                    "waiting": waiting,
                    "serving": serving, 
                    "completed": completed,
                    "total": waiting + serving + completed
                }
            }
        except Exception as e:
            logger.error(f"Error in get_queue_status: {e}")
            return {"success": False, "error": str(e)}
    
    def get_my_schedule(self, week_offset: int = 0) -> Dict[str, Any]:
        """Get personal schedule for a specific week"""
        try:
            today = date.today()
            week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
            week_end = week_start + timedelta(days=6)
            
            schedules = self.db.query(StaffSchedule).filter(
                and_(
                    StaffSchedule.staff_id == self.user_id,
                    StaffSchedule.scheduled_date >= week_start,
                    StaffSchedule.scheduled_date <= week_end
                )
            ).all()
            
            schedule_list = []
            for s in schedules:
                shift = self.db.query(Shift).filter(Shift.id == s.shift_id).first()
                schedule_list.append({
                    "date": s.scheduled_date.isoformat(),
                    "day": s.scheduled_date.strftime("%A"),
                    "shift_name": shift.name if shift else "Unknown",
                    "start_time": shift.start_time.strftime("%H:%M") if shift else "",
                    "end_time": shift.end_time.strftime("%H:%M") if shift else "",
                    "status": s.status
                })
            
            return {
                "success": True,
                "data": {
                    "week_start": week_start.isoformat(),
                    "week_end": week_end.isoformat(),
                    "total_shifts": len(schedule_list),
                    "schedules": schedule_list
                }
            }
        except Exception as e:
            logger.error(f"Error in get_my_schedule: {e}")
            return {"success": False, "error": str(e)}
    
    def get_my_performance(self, days: int = 7) -> Dict[str, Any]:
        """Get personal performance statistics"""
        try:
            start_date = date.today() - timedelta(days=days)
            
            tickets = self.db.query(QueueTicket).filter(
                and_(
                    QueueTicket.staff_id == self.user_id,
                    QueueTicket.status == TicketStatus.completed,
                    func.date(QueueTicket.created_at) >= start_date
                )
            ).all()
            
            total_served = len(tickets)
            ratings = [t.overall_rating for t in tickets if t.overall_rating and t.overall_rating > 0]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            return {
                "success": True,
                "data": {
                    "period_days": days,
                    "total_served": total_served,
                    "average_rating": round(avg_rating, 1),
                    "total_ratings": len(ratings)
                }
            }
        except Exception as e:
            logger.error(f"Error in get_my_performance: {e}")
            return {"success": False, "error": str(e)}
    
    def get_department_stats(self) -> Dict[str, Any]:
        """Get department statistics (Manager only)"""
        if self.user_role != 'manager':
            return {"success": False, "error": "Permission denied"}
        
        try:
            today = date.today()
            
            # Get all staff in department
            staff_list = self.db.query(User).filter(
                and_(
                    User.department_id == self.department_id,
                    User.role == 'staff'
                )
            ).all()
            
            staff_ids = [s.id for s in staff_list]
            
            # Get today's tickets for department
            tickets_today = self.db.query(QueueTicket).filter(
                and_(
                    QueueTicket.staff_id.in_(staff_ids),
                    func.date(QueueTicket.created_at) == today
                )
            ).all()
            
            completed = len([t for t in tickets_today if t.status == TicketStatus.completed])
            waiting = len([t for t in tickets_today if t.status == TicketStatus.waiting])
            
            return {
                "success": True,
                "data": {
                    "total_staff": len(staff_list),
                    "tickets_today": len(tickets_today),
                    "completed_today": completed,
                    "waiting": waiting
                }
            }
        except Exception as e:
            logger.error(f"Error in get_department_stats: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_staff_status(self) -> Dict[str, Any]:
        """Get status of all staff in department (Manager only)"""
        if self.user_role != 'manager':
            return {"success": False, "error": "Permission denied"}
        
        try:
            from datetime import datetime
            
            staff_list = self.db.query(User).filter(
                and_(
                    User.department_id == self.department_id,
                    User.role == 'staff'
                )
            ).all()
            
            result = []
            for staff in staff_list:
                # Check if online (logged in within 30 mins)
                is_online = False
                if staff.last_login:
                    delta = datetime.utcnow() - staff.last_login
                    is_online = delta.total_seconds() < 1800
                
                result.append({
                    "id": staff.id,
                    "name": staff.full_name,
                    "username": staff.username,
                    "status": "online" if is_online else "offline"
                })
            
            online_count = len([s for s in result if s["status"] == "online"])
            
            return {
                "success": True,
                "data": {
                    "total_staff": len(result),
                    "online": online_count,
                    "offline": len(result) - online_count,
                    "staff_list": result
                }
            }
        except Exception as e:
            logger.error(f"Error in get_all_staff_status: {e}")
            return {"success": False, "error": str(e)}
    
    def execute_function(self, function_name: str, args: Dict = None) -> Dict[str, Any]:
        """Execute a function by name with given arguments"""
        args = args or {}
        
        function_map = {
            "get_queue_status": lambda: self.get_queue_status(),
            "get_my_schedule": lambda: self.get_my_schedule(args.get("week_offset", 0)),
            "get_my_performance": lambda: self.get_my_performance(args.get("days", 7)),
            "get_department_stats": lambda: self.get_department_stats(),
            "get_all_staff_status": lambda: self.get_all_staff_status(),
        }
        
        if function_name in function_map:
            logger.info(f"Executing AI function: {function_name} with args: {args}")
            return function_map[function_name]()
        else:
            return {"success": False, "error": f"Unknown function: {function_name}"}


# Tool declarations for Gemini API
TOOL_DECLARATIONS = [
    {
        "name": "get_queue_status",
        "description": "Lấy trạng thái hàng đợi hiện tại hôm nay (số khách đang chờ, đang phục vụ, đã hoàn thành)",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_my_schedule",
        "description": "Lấy lịch làm việc cá nhân theo tuần",
        "parameters": {
            "type": "object",
            "properties": {
                "week_offset": {
                    "type": "integer",
                    "description": "0 = tuần này, 1 = tuần sau, -1 = tuần trước"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_my_performance",
        "description": "Lấy thống kê hiệu suất cá nhân (số phiếu đã phục vụ, đánh giá trung bình)",
        "parameters": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Số ngày cần thống kê (mặc định 7 ngày)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_department_stats",
        "description": "Lấy thống kê phòng ban (chỉ dành cho Manager)",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_all_staff_status",
        "description": "Lấy trạng thái online/offline của tất cả nhân viên trong phòng ban (chỉ dành cho Manager)",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]
