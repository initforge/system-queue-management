# Test SQL Generation AI Helper

## ✅ Implementation Complete

### Files Modified:
1. **backend/app/utils/sql_validator.py** (NEW)
   - SQLValidator class với validate() và add_limit()
   - DATABASE_SCHEMA constant với full schema documentation
   
2. **backend/app/services/gemini_service.py**
   - Updated MODELS_TO_TRY: gemini-2.5-flash-lite (unlimited RPM)
   - Added `sql_mode` parameter to generate_response()
   - Enhanced _build_system_prompt() với SQL generation instructions
   
3. **backend/app/api/v1/ai_helper.py**
   - Added `mode` parameter (default: "sql")
   - SQL extraction from ```sql...``` blocks
   - SQL validation & execution
   - Result formatting

---

## 🧪 Test Cases

### Test 1: Đếm khách đang chờ
**Request:**
```json
POST /api/v1/ai-helper/chat
{
  "message": "Hàng đợi có bao nhiêu người?",
  "api_key": "YOUR_GEMINI_KEY",
  "mode": "sql"
}
```

**Expected AI Response:**
```sql
SELECT COUNT(*) FROM queue_tickets WHERE status = 'waiting'
```

---

### Test 2: Top nhân viên
**Request:**
```json
{
  "message": "Top 3 nhân viên có rating cao nhất?",
  "api_key": "YOUR_GEMINI_KEY",
  "mode": "sql"
}
```

**Expected:**
```sql
SELECT u.full_name, sp.avg_rating, sp.tickets_served 
FROM staff_performance sp 
JOIN users u ON sp.staff_id = u.id 
ORDER BY sp.avg_rating DESC LIMIT 3
```

---

### Test 3: Tổng khách hôm nay
**Request:**
```json
{
  "message": "Hôm nay phục vụ được bao nhiêu khách?",
  "api_key": "YOUR_GEMINI_KEY",
  "mode": "sql"
}
```

**Expected:**
```sql
SELECT COUNT(*) FROM queue_tickets 
WHERE DATE(created_at) = CURRENT_DATE 
AND status = 'completed'
```

---

### Test 4: Ca làm việc
**Request:**
```json
{
  "message": "Ai làm ca sáng hôm nay?",
  "api_key": "YOUR_GEMINI_KEY",
  "mode": "sql"
}
```

**Expected:**
```sql
SELECT u.full_name, s.name, s.start_time, s.end_time
FROM staff_schedules ss
JOIN users u ON ss.staff_id = u.id
JOIN shifts s ON ss.shift_id = s.id
WHERE ss.scheduled_date = CURRENT_DATE 
AND s.shift_type = 'morning'
```

---

### Test 5: Non-data question (should NOT generate SQL)
**Request:**
```json
{
  "message": "Chào bạn, hệ thống có những tính năng gì?",
  "api_key": "YOUR_GEMINI_KEY",
  "mode": "sql"
}
```

**Expected:** Normal text response without SQL query

---

## 🔒 Security Features

✅ **SQL Validation:**
- Only SELECT queries allowed
- Blacklist: DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, EXEC
- No SQL comments (--,  /*)
- No multiple statements

✅ **Role-based Access:**
- Staff: WHERE staff_id = current_user.id
- Manager: WHERE department_id = current_user.department_id

✅ **Performance:**
- Auto LIMIT 100 rows
- 5-second timeout (configurable)
- Query result max 10 rows display

---

## 📊 Response Format

```json
{
  "message": "Hiện có 15 người đang chờ trong hàng đợi.\n\n📊 **Kết quả:**\n1. count: 15",
  "conversation_id": "uuid",
  "timestamp": "2026-01-09T...",
  "sql_query": "SELECT COUNT(*) FROM queue_tickets WHERE status = 'waiting' LIMIT 100",
  "query_result": [{"count": 15}],
  "error": null
}
```

---

## 🎯 Usage in Frontend

```javascript
// Enable SQL mode (default)
const response = await fetch('/api/v1/ai-helper/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "Hàng đợi có bao nhiêu người?",
    api_key: userApiKey,
    mode: "sql"  // or "chat" for normal mode
  })
});

// Response includes:
// - message: Formatted answer
// - sql_query: The executed SQL
// - query_result: Raw data array
```

---

## ⚠️ Known Limitations

1. **Model availability:** gemini-2.5-flash-lite might not be available yet
   - Fallback to gemini-2.5-flash or gemini-1.5-pro
   
2. **Complex joins:** AI may struggle with 3+ table joins
   - Provide examples in DATABASE_SCHEMA for common queries
   
3. **Time zones:** All timestamps in UTC
   - Frontend should handle timezone conversion

---

## 🚀 Next Steps

1. Test với real API key trên frontend
2. Add conversation history support
3. Optimize database schema prompt với common patterns
4. Add query caching (Redis) cho repeated queries
5. Implement query performance monitoring
