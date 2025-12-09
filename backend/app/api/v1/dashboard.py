from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from ...core.database import get_db
from ...models import (
    QueueTicket, Service, Department, User, TicketStatus, 
    TicketPriority, ServiceSession, Feedback
)
from ...core.security import get_current_user

router = APIRouter()

# Pydantic models
class DashboardStats(BaseModel):
    total_tickets_today: int
    tickets_completed_today: int
    tickets_waiting: int
    tickets_serving: int
    average_wait_time: float
    customer_satisfaction: float
    total_departments: int
    active_staff: int

class DepartmentStats(BaseModel):
    department_id: int
    department_name: str
    total_tickets: int
    completed_tickets: int
    waiting_tickets: int
    serving_tickets: int
    average_wait_time: float
    customer_satisfaction: float

class StaffPerformance(BaseModel):
    staff_id: int
    staff_name: str
    department_name: str
    tickets_served: int
    average_service_time: float
    customer_satisfaction: float
    total_working_hours: float

class QueueAnalytics(BaseModel):
    hourly_distribution: List[Dict[str, Any]]
    service_distribution: List[Dict[str, Any]]
    wait_time_distribution: List[Dict[str, Any]]
    priority_distribution: List[Dict[str, Any]]

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = datetime.now().date()
    
    # Total tickets today
    total_tickets_today = await db.execute(
        select(func.count(QueueTicket.id))
        .where(func.date(QueueTicket.created_at) == today)
    )
    total_tickets_today_count = total_tickets_today.scalar()
    
    # Completed tickets today
    completed_tickets_today = await db.execute(
        select(func.count(QueueTicket.id))
        .where(
            and_(
                func.date(QueueTicket.created_at) == today,
                QueueTicket.status == TicketStatus.completed
            )
        )
    )
    completed_tickets_today_count = completed_tickets_today.scalar()
    
    # Current waiting tickets
    waiting_tickets = await db.execute(
        select(func.count(QueueTicket.id))
        .where(QueueTicket.status == TicketStatus.waiting)
    )
    waiting_tickets_count = waiting_tickets.scalar()
    
    # Current serving tickets
    serving_tickets = await db.execute(
        select(func.count(QueueTicket.id))
        .where(QueueTicket.status == TicketStatus.completed)
    )
    serving_tickets_count = serving_tickets.scalar()
    
    # Average wait time (in minutes)
    avg_wait_time = await db.execute(
        select(func.avg(QueueTicket.estimated_wait_time))
        .where(
            and_(
                func.date(QueueTicket.created_at) == today,
                QueueTicket.status == TicketStatus.completed
            )
        )
    )
    avg_wait_time_value = avg_wait_time.scalar() or 0
    
    # Customer satisfaction
    customer_satisfaction = await db.execute(
        select(func.avg(Feedback.rating))
        .where(func.date(Feedback.created_at) == today)
    )
    customer_satisfaction_value = customer_satisfaction.scalar() or 0
    
    # Total departments
    total_departments = await db.execute(
        select(func.count(Department.id))
        .where(Department.is_active == True)
    )
    total_departments_count = total_departments.scalar()
    
    # Active staff (logged in today)
    active_staff = await db.execute(
        select(func.count(User.id))
        .where(
            and_(
                User.is_active == True,
                User.role == 'staff',
                func.date(User.last_login) == today
            )
        )
    )
    active_staff_count = active_staff.scalar()
    
    return DashboardStats(
        total_tickets_today=total_tickets_today_count,
        tickets_completed_today=completed_tickets_today_count,
        tickets_waiting=waiting_tickets_count,
        tickets_serving=serving_tickets_count,
        average_wait_time=float(avg_wait_time_value),
        customer_satisfaction=float(customer_satisfaction_value),
        total_departments=total_departments_count,
        active_staff=active_staff_count
    )

@router.get("/departments", response_model=List[DepartmentStats])
async def get_department_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    today = datetime.now().date()
    
    # Get all departments
    departments_result = await db.execute(
        select(Department)
        .where(Department.is_active == True)
        .order_by(Department.name)
    )
    departments = departments_result.scalars().all()
    
    department_stats = []
    for dept in departments:
        # Total tickets
        total_tickets = await db.execute(
            select(func.count(QueueTicket.id))
            .where(
                and_(
                    QueueTicket.department_id == dept.id,
                    func.date(QueueTicket.created_at) == today
                )
            )
        )
        total_tickets_count = total_tickets.scalar()
        
        # Completed tickets
        completed_tickets = await db.execute(
            select(func.count(QueueTicket.id))
            .where(
                and_(
                    QueueTicket.department_id == dept.id,
                    func.date(QueueTicket.created_at) == today,
                    QueueTicket.status == TicketStatus.completed
                )
            )
        )
        completed_tickets_count = completed_tickets.scalar()
        
        # Waiting tickets
        waiting_tickets = await db.execute(
            select(func.count(QueueTicket.id))
            .where(
                and_(
                    QueueTicket.department_id == dept.id,
                    QueueTicket.status == TicketStatus.waiting
                )
            )
        )
        waiting_tickets_count = waiting_tickets.scalar()
        
        # Serving tickets
        serving_tickets = await db.execute(
            select(func.count(QueueTicket.id))
            .where(
                and_(
                    QueueTicket.department_id == dept.id,
                    QueueTicket.status == TicketStatus.completed
                )
            )
        )
        serving_tickets_count = serving_tickets.scalar()
        
        # Average wait time
        avg_wait_time = await db.execute(
            select(func.avg(QueueTicket.estimated_wait_time))
            .where(
                and_(
                    QueueTicket.department_id == dept.id,
                    func.date(QueueTicket.created_at) == today,
                    QueueTicket.status == TicketStatus.completed
                )
            )
        )
        avg_wait_time_value = avg_wait_time.scalar() or 0
        
        # Customer satisfaction
        customer_satisfaction = await db.execute(
            select(func.avg(Feedback.rating))
            .join(QueueTicket)
            .where(
                and_(
                    QueueTicket.department_id == dept.id,
                    func.date(Feedback.created_at) == today
                )
            )
        )
        customer_satisfaction_value = customer_satisfaction.scalar() or 0
        
        department_stats.append(DepartmentStats(
            department_id=dept.id,
            department_name=dept.name,
            total_tickets=total_tickets_count,
            completed_tickets=completed_tickets_count,
            waiting_tickets=waiting_tickets_count,
            serving_tickets=serving_tickets_count,
            average_wait_time=float(avg_wait_time_value),
            customer_satisfaction=float(customer_satisfaction_value)
        ))
    
    return department_stats

@router.get("/staff-performance", response_model=List[StaffPerformance])
async def get_staff_performance(
    department_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    today = datetime.now().date()
    
    # Query staff members
    query = select(User, Department).join(Department, User.department_id == Department.id)
    query = query.where(
        and_(
            User.role == 'staff',
            User.is_active == True
        )
    )
    
    if department_id:
        query = query.where(User.department_id == department_id)
    
    staff_result = await db.execute(query.order_by(User.full_name))
    staff_members = staff_result.all()
    
    performance_stats = []
    for staff, department in staff_members:
        # Tickets served today
        tickets_served = await db.execute(
            select(func.count(QueueTicket.id))
            .where(
                and_(
                    QueueTicket.staff_id == staff.id,
                    func.date(QueueTicket.completed_at) == today,
                    QueueTicket.status == TicketStatus.completed
                )
            )
        )
        tickets_served_count = tickets_served.scalar()
        
        # Average service time
        avg_service_time = await db.execute(
            select(func.avg(ServiceSession.duration))
            .where(
                and_(
                    ServiceSession.staff_id == staff.id,
                    func.date(ServiceSession.started_at) == today,
                    ServiceSession.status == 'completed'
                )
            )
        )
        avg_service_time_value = avg_service_time.scalar() or 0
        
        # Customer satisfaction
        customer_satisfaction = await db.execute(
            select(func.avg(Feedback.rating))
            .where(
                and_(
                    Feedback.staff_id == staff.id,
                    func.date(Feedback.created_at) == today
                )
            )
        )
        customer_satisfaction_value = customer_satisfaction.scalar() or 0
        
        # Total working hours
        total_working_hours = await db.execute(
            select(func.sum(ServiceSession.duration))
            .where(
                and_(
                    ServiceSession.staff_id == staff.id,
                    func.date(ServiceSession.started_at) == today
                )
            )
        )
        total_working_hours_value = (total_working_hours.scalar() or 0) / 60  # Convert to hours
        
        performance_stats.append(StaffPerformance(
            staff_id=staff.id,
            staff_name=staff.full_name,
            department_name=department.name,
            tickets_served=tickets_served_count,
            average_service_time=float(avg_service_time_value),
            customer_satisfaction=float(customer_satisfaction_value),
            total_working_hours=float(total_working_hours_value)
        ))
    
    return performance_stats

@router.get("/analytics", response_model=QueueAnalytics)
async def get_queue_analytics(
    department_id: Optional[int] = None,
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Hourly distribution
    hourly_query = select(
        func.extract('hour', QueueTicket.created_at).label('hour'),
        func.count(QueueTicket.id).label('count')
    ).where(
        QueueTicket.created_at.between(start_date, end_date)
    ).group_by(func.extract('hour', QueueTicket.created_at))
    
    if department_id:
        hourly_query = hourly_query.where(QueueTicket.department_id == department_id)
    
    hourly_result = await db.execute(hourly_query)
    hourly_distribution = [
        {"hour": int(hour), "count": count}
        for hour, count in hourly_result
    ]
    
    # Service distribution
    service_query = select(
        Service.name,
        func.count(QueueTicket.id).label('count')
    ).join(Service).where(
        QueueTicket.created_at.between(start_date, end_date)
    ).group_by(Service.name)
    
    if department_id:
        service_query = service_query.where(QueueTicket.department_id == department_id)
    
    service_result = await db.execute(service_query)
    service_distribution = [
        {"service": name, "count": count}
        for name, count in service_result
    ]
    
    # Wait time distribution
    wait_time_query = select(
        func.case(
            (QueueTicket.estimated_wait_time < 15, '< 15 min'),
            (QueueTicket.estimated_wait_time < 30, '15-30 min'),
            (QueueTicket.estimated_wait_time < 60, '30-60 min'),
            else_='> 60 min'
        ).label('wait_range'),
        func.count(QueueTicket.id).label('count')
    ).where(
        and_(
            QueueTicket.created_at.between(start_date, end_date),
            QueueTicket.estimated_wait_time.isnot(None)
        )
    ).group_by('wait_range')
    
    if department_id:
        wait_time_query = wait_time_query.where(QueueTicket.department_id == department_id)
    
    wait_time_result = await db.execute(wait_time_query)
    wait_time_distribution = [
        {"range": range_name, "count": count}
        for range_name, count in wait_time_result
    ]
    
    # Priority distribution
    priority_query = select(
        QueueTicket.priority,
        func.count(QueueTicket.id).label('count')
    ).where(
        QueueTicket.created_at.between(start_date, end_date)
    ).group_by(QueueTicket.priority)
    
    if department_id:
        priority_query = priority_query.where(QueueTicket.department_id == department_id)
    
    priority_result = await db.execute(priority_query)
    priority_distribution = [
        {"priority": priority, "count": count}
        for priority, count in priority_result
    ]
    
    return QueueAnalytics(
        hourly_distribution=hourly_distribution,
        service_distribution=service_distribution,
        wait_time_distribution=wait_time_distribution,
        priority_distribution=priority_distribution
    )
