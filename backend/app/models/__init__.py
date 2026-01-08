"""
Minimal models for Queue Management System
Tables: 9 (departments, users, services, counters, queue_tickets, 
        staff_performance, ticket_complaints, shifts, staff_schedules)
"""

from ..core.database import Base

from .user import User
from .department import Department
from .service import Service
from .counter import Counter
from .ticket import QueueTicket, TicketStatus, TicketPriority
from .ticket_complaint import TicketComplaint, TicketComplaintStatus
from .schedule import Shift, StaffSchedule
from .staff_performance import StaffPerformance

__all__ = [
    "Base",
    "User", 
    "Department",
    "Service",
    "Counter",
    "QueueTicket",
    "TicketStatus",
    "TicketPriority",
    "TicketComplaint",
    "TicketComplaintStatus", 
    "Shift",
    "StaffSchedule",
    "StaffPerformance",
]