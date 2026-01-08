"""
SQL Validator for AI-generated queries
Ensures safe execution of SELECT queries only
"""
import re
from typing import Tuple, Optional


class SQLValidator:
    """Validates SQL queries for safe execution"""
    
    # Dangerous keywords that could modify data
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
        'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE',
        'EXEC', 'EXECUTE', 'CALL', 'PRAGMA'
    ]
    
    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r'--',  # SQL comments
        r'/\*',  # Multi-line comments
        r';.*(?:DROP|DELETE|UPDATE|INSERT)',  # Multiple statements
    ]
    
    @staticmethod
    def validate(sql: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for safe execution
        
        Args:
            sql: SQL query string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not sql or not sql.strip():
            return False, "Query is empty"
        
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed"
        
        # Check for dangerous keywords
        for keyword in SQLValidator.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return False, f"Dangerous keyword detected: {keyword}"
        
        # Check for dangerous patterns
        for pattern in SQLValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return False, f"Dangerous pattern detected: {pattern}"
        
        # Check for multiple statements (simple check)
        if sql.count(';') > 1:
            return False, "Multiple statements not allowed"
        
        return True, None
    
    @staticmethod
    def add_limit(sql: str, max_rows: int = 100) -> str:
        """
        Add LIMIT clause if not present
        
        Args:
            sql: SQL query string
            max_rows: Maximum rows to return
            
        Returns:
            SQL with LIMIT clause
        """
        sql = sql.strip().rstrip(';')
        sql_upper = sql.upper()
        
        if 'LIMIT' not in sql_upper:
            sql += f" LIMIT {max_rows}"
        
        return sql


# Database schema context for AI
DATABASE_SCHEMA = """
=== DATABASE SCHEMA ===

TABLE: users
- id (INTEGER, PRIMARY KEY)
- username (VARCHAR)
- full_name (VARCHAR)
- email (VARCHAR)
- phone (VARCHAR)
- role (ENUM: 'admin', 'manager', 'staff')
- department_id (INTEGER, FOREIGN KEY → departments.id)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

TABLE: departments
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR)
- code (VARCHAR)
- description (TEXT)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

TABLE: services
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR)
- description (TEXT)
- department_id (INTEGER, FOREIGN KEY → departments.id)
- service_code (VARCHAR)
- estimated_duration (INTEGER, minutes)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

TABLE: counters
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR)
- number (INTEGER)
- department_id (INTEGER, FOREIGN KEY → departments.id)
- assigned_staff_id (INTEGER, FOREIGN KEY → users.id)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)

TABLE: queue_tickets
- id (INTEGER, PRIMARY KEY) -- NOT UUID!
- ticket_number (VARCHAR)
- customer_name (VARCHAR)
- customer_phone (VARCHAR)
- customer_email (VARCHAR)
- service_id (INTEGER, FOREIGN KEY → services.id)
- department_id (INTEGER, FOREIGN KEY → departments.id)
- staff_id (INTEGER, FOREIGN KEY → users.id)
- counter_id (INTEGER, FOREIGN KEY → counters.id)
- status (ENUM: 'waiting', 'called', 'completed', 'no_show')
- priority (ENUM: 'normal', 'high', 'elderly', 'disabled', 'vip')
- queue_position (INTEGER)
- form_data (JSONB)
- notes (TEXT)
- estimated_wait_time (INTEGER)
- created_at (TIMESTAMP)
- called_at (TIMESTAMP)
- served_at (TIMESTAMP)
- completed_at (TIMESTAMP)
- overall_rating (INTEGER, 1-5)
- review_comments (TEXT)
- reviewed_at (TIMESTAMP)

TABLE: staff_performance
- id (INTEGER, PRIMARY KEY)
- user_id (INTEGER, FOREIGN KEY → users.id) -- NOT staff_id!
- department_id (INTEGER, FOREIGN KEY → departments.id)
- date (DATE)
- tickets_served (INTEGER)
- avg_service_time (NUMERIC, seconds)
- total_rating_score (INTEGER)
- rating_count (INTEGER)
- avg_rating (NUMERIC)
- created_at (TIMESTAMP)

TABLE: ticket_complaints
- id (INTEGERINTEGER, FOREIGN KEY → queue_tickets.id)
- customer_name (VARCHAR)
- customer_phone (VARCHAR)
- customer_email (VARCHAR)
- complaint_text (TEXT)
- rating (INTEGER)
- status (VARCHAR, default 'waiting')
- assigned_to (INTEGER, FOREIGN KEY → users.id)
- manager_response (TEXT)
- created_at (TIMESTAMP)
- resolvs (ENUM: 'pending', 'resolved', 'rejected')
- created_at (TIMESTAMP)

TABLE: shifts
- id (INTEGER, PRIMARY KEY)
- name (VARCHAR)
- shift_type (ENUM: 'morning', 'afternoon', 'night', 'other')
- starINTEGER, PRIMARY KEY) -- NOT UUID!
- staff_id (INTEGER, FOREIGN KEY → users.id)
- manager_id (INTEGER, FOREIGN KEY → users.id)
- shift_id (INTEGER, FOREIGN KEY → shifts.id)
- scheduled_date (DATE)
- status (shift_status ff_schedules
- id (UUID, PRIMARY KEY)
- staff_id (INTEGER, FOREIGN KEY → users.id)
- manager_id (INTEGER, FOREIGN KEY → users.id)
- shift_id (INTEGER, FOREIGN KEY → shifts.id)
- scheduled_date (DATE)
- status (ENUM: 'scheduled', 'confirmed', 'cancelled', 'completed')
- notes (TEXT)
- created_at (TIMESTAMP)

=== COMMON QUERIES ===

Đếm số khách đang cuser
SELECT COUNT(*) FROM queue_tickets WHERE status = 'waiting'

Top nhân viên theo theo status:
SELECT status, COUNT(*) as total FROM queue_tickets 
WHERE DATE(created_at) = CURRENT_DATE 
GROUP BY status

Tổng khách đã phục vụ hôm nay:
SELECT COUNT(*) FROM queue_tickets 
WHERE DATE(created_at) = CURRENT_DATE AND status = 'completed'
FROM staff_performance sp 
JOIN users u ON sp.staff_id = u.id 
ORDER BY sp.avg_rating DESC LIMIT 5

Tổng khách hôm nay:
SELECT COUNT(*) FROM queue_tickets WHERE DATE(created_at) = CURRENT_DATE

Ca làm việc hôm nay:
SELECT u.full_name, s.name, s.start_time, s.end_time
FROM staff_schedules ss
JOIN users u ON ss.staff_id = u.id
JOIN shifts s ON ss.shift_id = s.id
WHERE ss.scheduled_date = CURRENT_DATE

Trung bình thời gian phục vụ:
SELECT AVG(EXTRACT(EPOCH FROM (completed_at - called_at))) as avg_seconds
FROM queue_tickets 
WHERE status = 'completed' AND called_at IS NOT NULL
"""
