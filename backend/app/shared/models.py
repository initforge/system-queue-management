from sqlalchemy.ext.declarative import declarative_base
import enum

# Base model class - single source of truth
Base = declarative_base()

# Common enums that might be used across domains
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"

class TicketStatus(str, enum.Enum):
    WAITING = "waiting"
    CALLED = "called"
    SERVING = "serving"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class TicketPriority(str, enum.Enum):
    NORMAL = "normal"
    HIGH = "high"
    ELDERLY = "elderly"
    DISABLED = "disabled"
    VIP = "vip"

class FieldType(str, enum.Enum):
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    NUMBER = "number"
    DATE = "date"

# Schedule-related enums
class ShiftType(str, enum.Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"

class ShiftStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class LeaveType(str, enum.Enum):
    SICK = "sick"
    PERSONAL = "personal"
    VACATION = "vacation"
    EMERGENCY = "emergency"

class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class CheckinStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"