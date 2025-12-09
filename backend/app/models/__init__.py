"""
Core models for the Queue Management System
"""

from ..core.database import declarative_base
Base = declarative_base()

from .user import User
from .department import Department
from .service import Service
from .ticket import QueueTicket, TicketStatus, TicketPriority
from .ticket_complaint import TicketComplaint, TicketComplaintStatus
from .feedback import Feedback
from .notification import StaffNotification
from .daily_login_log import DailyLoginLog
from .schedule import Shift, StaffSchedule, LeaveRequest, ShiftExchange, StaffCheckin, StaffAttendance
from .ai_conversation import AIConversation
from .knowledge_base import KnowledgeBaseCategory, KnowledgeBaseArticle, KnowledgeBaseAttachment
from .qr_code import QRCode
from .service_session import ServiceSession

# Note: Schedule-related models (Shift, StaffSchedule, LeaveRequest, etc.) 
# are still in models.py file and can be imported via __getattr__ if needed
# For now, we only need DailyLoginLog which is now in this package
def _import_models_from_file():
    """Lazy import of models from models.py file - simplified to avoid conflicts"""
    # Return empty dict - schedule models should be imported directly from models.py
    # This avoids conflicts with DailyLoginLog which is now in models/daily_login_log.py
    return {}
    
    # Original complex logic disabled to avoid import conflicts
    # TODO: Re-enable or refactor when schedule models are properly separated into package
    try:
        import sys
        import importlib.util
        from pathlib import Path
        
        app_dir = Path(__file__).parent.parent
        models_py_path = app_dir / 'models.py'
        
        if not models_py_path.exists():
            return {}
        
        # Use a unique module name to avoid conflicts
        module_name = "app._models_py_file"
        if module_name not in sys.modules:
            spec = importlib.util.spec_from_file_location(
                module_name, 
                str(models_py_path),
                submodule_search_locations=[str(app_dir)]
            )
            if spec and spec.loader:
                # Temporarily add app_dir to sys.path to allow relative imports
                old_path = sys.path[:]
                app_dir_str = str(app_dir)
                if app_dir_str not in sys.path:
                    sys.path.insert(0, app_dir_str)
                
                try:
                    # Read models.py and only extract the models we need (Schedule-related models)
                    # Skip User, Department, Service, etc. that are already in models/ package
                    from app.core.database import Base
                    from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Date, Time, UniqueConstraint
                    from sqlalchemy.orm import relationship
                    from sqlalchemy.sql import func
                    from datetime import datetime
                    import enum
                    import uuid
                    from sqlalchemy.dialects.postgresql import UUID, ENUM
                    
                    # Read file to find where schedule models start
                    with open(models_py_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find the line where schedule models start (Shift class)
                    # Extract only from "class Shift" onwards to avoid redefining User, Department, etc.
                    shift_start = content.find('class Shift(Base):')
                    if shift_start == -1:
                        raise ImportError("Could not find Shift class in models.py")
                    
                    # Find where DailyLoginLog starts - we MUST skip it since it's now in models/daily_login_log.py
                    # Search more thoroughly for DailyLoginLog class definition
                    daily_login_start = content.find('\nclass DailyLoginLog(Base):', shift_start)
                    if daily_login_start == -1:
                        daily_login_start = content.find('\nclass DailyLoginLog (Base):', shift_start)
                    if daily_login_start == -1:
                        # Try without newline at start
                        temp_pos = content.find('class DailyLoginLog(Base):', shift_start)
                        if temp_pos > 0 and content[temp_pos-1] == '\n':
                            daily_login_start = temp_pos - 1
                    
                    # Also check for comment marker before DailyLoginLog
                    if daily_login_start == -1:
                        ai_comment = content.find('\n# AI Conversation Model', shift_start)
                        if ai_comment != -1:
                            schedule_end = ai_comment
                        else:
                            # Last resort: search backwards from a known point
                            schedule_end = len(content)
                            # Try to find end of StaffAttendance class
                            staff_attendance_end = content.find('class DailyLoginLog', shift_start)
                            if staff_attendance_end != -1:
                                # Go back to find the end of previous class
                                schedule_end = staff_attendance_end
                    else:
                        schedule_end = daily_login_start
                    
                    # Extract enum definitions before Shift (lines ~295-305)
                    enum_start = content.find('shift_type_enum = ENUM')
                    if enum_start == -1:
                        enum_start = shift_start
                    
                    enum_section = content[enum_start:shift_start]
                    
                    # Extract schedule models section (from Shift to before DailyLoginLog)
                    schedule_section = content[shift_start:schedule_end]
                    
                    # CRITICAL: Remove any DailyLoginLog definition that might have slipped in
                    # Use regex-like splitting to ensure we remove everything related to DailyLoginLog
                    if 'DailyLoginLog' in schedule_section:
                        # Split by class definitions and filter out DailyLoginLog
                        import re
                        # Remove the entire DailyLoginLog class block
                        pattern = r'\nclass DailyLoginLog\(Base\):.*?(?=\nclass |\n# |\Z)'
                        schedule_section = re.sub(pattern, '', schedule_section, flags=re.DOTALL)
                        # Also remove any remaining references
                        schedule_section = re.sub(r'.*DailyLoginLog.*\n?', '', schedule_section)
                    
                    # Prepare minimal code with only what we need
                    minimal_code = f"""# Schedule-related models only
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Date, Time, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID, ENUM
from app.core.database import Base

# Enum definitions
{enum_section}

# Schedule models (only models not in models/ package)
{schedule_section}
"""
                    
                    # Create namespace with Base and all dependencies
                    namespace = {
                        'Column': Column,
                        'Integer': Integer,
                        'String': String,
                        'Boolean': Boolean,
                        'DateTime': DateTime,
                        'Text': Text,
                        'ForeignKey': ForeignKey,
                        'JSON': JSON,
                        'Enum': SQLEnum,
                        'SQLEnum': SQLEnum,
                        'Date': Date,
                        'Time': Time,
                        'UniqueConstraint': UniqueConstraint,
                        'relationship': relationship,
                        'func': func,
                        'datetime': datetime,
                        'enum': enum,
                        'uuid': uuid,
                        'UUID': UUID,
                        'ENUM': ENUM,
                        'Base': Base,
                    }
                    
                    # Exec only the schedule models code
                    compiled = compile(minimal_code, str(models_py_path), 'exec')
                    exec(compiled, namespace)
                    
                    # Create module object
                    models_file = importlib.util.module_from_spec(spec)
                    models_file.__dict__.update(namespace)
                    models_file.__package__ = 'app'
                    models_file.__file__ = str(models_py_path)
                    
                    # Store in sys.modules
                    sys.modules[module_name] = models_file
                except Exception as exec_error:
                    # If exec fails, try to handle it gracefully
                    import warnings
                    warnings.warn(f"Error executing models.py: {exec_error}")
                    import traceback
                    traceback.print_exc()
                    raise
                finally:
                    # Restore sys.path
                    sys.path[:] = old_path
                
                return {
                    # DailyLoginLog is now in models/daily_login_log.py, skip it
                    'StaffSchedule': getattr(models_file, 'StaffSchedule', None),
                    'Shift': getattr(models_file, 'Shift', None),
                    'LeaveRequest': getattr(models_file, 'LeaveRequest', None),
                    'StaffCheckin': getattr(models_file, 'StaffCheckin', None),
                    'StaffAttendance': getattr(models_file, 'StaffAttendance', None),
                    # AI and Knowledge Base models come after DailyLoginLog, extract separately if needed
                }
        else:
            models_file = sys.modules[module_name]
            return {
                # DailyLoginLog is now in models/daily_login_log.py, skip it
                'StaffSchedule': getattr(models_file, 'StaffSchedule', None),
                'Shift': getattr(models_file, 'Shift', None),
                'LeaveRequest': getattr(models_file, 'LeaveRequest', None),
                'StaffCheckin': getattr(models_file, 'StaffCheckin', None),
                'StaffAttendance': getattr(models_file, 'StaffAttendance', None),
            }
    except Exception as e:
        # If import fails, return empty dict - models will be imported directly where needed
        import warnings
        warnings.warn(f"Could not import models from models.py: {e}")
        import traceback
        traceback.print_exc()
        return {}

# Export models from models.py file via __getattr__
# This allows lazy loading when needed
_models_cache = None

def __getattr__(name):
    """Lazy import of models from models.py file"""
    global _models_cache
    if _models_cache is None:
        _models_cache = _import_models_from_file()
    
    if name in _models_cache and _models_cache[name] is not None:
        return _models_cache[name]
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    "Base",
    "User", 
    "Department",
    "Service",
    "QueueTicket",
    "TicketStatus",
    "TicketComplaint",
    "TicketComplaintStatus", 
    "Feedback",
    "StaffNotification",
    "DailyLoginLog",
    "Shift",
    "StaffSchedule",
    "LeaveRequest",
    "ShiftExchange",
    "StaffCheckin",
    "StaffAttendance",
    "AIConversation",
    "KnowledgeBaseCategory",
    "KnowledgeBaseArticle",
    "KnowledgeBaseAttachment",
    "QRCode",
    "ServiceSession",
    "TicketPriority",
]