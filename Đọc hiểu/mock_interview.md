# 🎤 Mock Interview - Queue Management System

## 📋 Mục Lục
- [🟢 Beginner Level](#-beginner-level)
- [🟡 Intermediate Level](#-intermediate-level) 
- [🔴 Advanced Level](#-advanced-level)

---

## 🟢 Beginner Level

### Q1: Hãy giải thích Queue Management System này sử dụng những công nghệ gì?

**💡 Đáp án:**
- **Frontend:** React 18.2.0, React Router DOM, Axios, Socket.IO Client, Tailwind CSS
- **Backend:** FastAPI (Python), SQLAlchemy ORM, PostgreSQL database, Redis cache
- **DevOps:** Docker, Docker Compose, Nginx reverse proxy
- **Real-time:** WebSocket connection cho live updates
- **Authentication:** JWT tokens, role-based access control

**🔍 Giải thích chi tiết:**
- React được chọn vì component-based architecture, virtual DOM performance, và ecosystem phong phú
- FastAPI được chọn vì async/await support, automatic API documentation, và type safety
- PostgreSQL cho ACID compliance và complex queries
- Redis cho caching và WebSocket session management

---

### Q2: Context API trong React hoạt động như thế nào? Ưu nhược điểm là gì?

**💡 Đáp án:**
Context API cho phép share state giữa components mà không cần prop drilling.

**Cách hoạt động:**
```javascript
// 1. Tạo Context
const AuthContext = createContext();

// 2. Tạo Provider
const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);
  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
};

// 3. Sử dụng trong component
const { user, isAuthenticated } = useAuth();
```

**Ưu điểm:**
- Tránh prop drilling
- Centralized state management
- Native React solution

**Nhược điểm:**
- Re-render performance issues nếu overuse
- Debugging khó hơn Redux
- Không có middleware ecosystem

---

### Q3: Tại sao dự án sử dụng Docker? Lợi ích là gì?

**💡 Đáp án:**
Docker provides containerization - đóng gói ứng dụng và dependencies vào containers.

**Lợi ích:**
1. **Consistency:** "Works on my machine" → "Works everywhere"
2. **Isolation:** Mỗi service chạy trong environment riêng biệt
3. **Scalability:** Dễ dàng scale horizontal
4. **DevOps:** Simplified deployment và CI/CD
5. **Resource efficiency:** Containers nhẹ hơn VMs

**Trong dự án:**
```yaml
services:
  frontend:   # React app container
  backend:    # FastAPI container  
  db:         # PostgreSQL container
  redis:      # Redis cache container
  nginx:      # Reverse proxy container
```

---

### Q4: REST API là gì? Các HTTP methods được sử dụng như thế nào?

**💡 Đáp án:**
REST (Representational State Transfer) là architectural style cho web services.

**HTTP Methods trong dự án:**
- **GET:** Lấy data (tickets, departments, users)
- **POST:** Tạo mới (create ticket, login, register)
- **PUT:** Update toàn bộ resource
- **PATCH:** Update partial resource
- **DELETE:** Xóa resource

**Example endpoints:**
```
GET    /api/v1/tickets          # Lấy danh sách tickets
POST   /api/v1/tickets          # Tạo ticket mới
GET    /api/v1/tickets/{id}     # Lấy ticket cụ thể
PUT    /api/v1/tickets/{id}     # Update ticket
DELETE /api/v1/tickets/{id}     # Xóa ticket
```

**REST Principles:**
1. Stateless
2. Client-Server architecture
3. Cacheable
4. Uniform interface
5. Layered system

---

### Q5: WebSocket khác gì với HTTP request thông thường?

**💡 Đáp án:**

| Feature | HTTP Request | WebSocket |
|---------|-------------|-----------|
| **Connection** | Request-Response cycle | Persistent connection |
| **Direction** | Client → Server only | Bidirectional |
| **Protocol** | HTTP/HTTPS | ws:// hoặc wss:// |
| **Overhead** | Headers mỗi request | Low overhead sau handshake |
| **Use case** | API calls, page loads | Real-time updates |

**Trong Queue Management:**
```javascript
// HTTP - Lấy ticket data
const response = await axios.get('/api/v1/tickets');

// WebSocket - Real-time queue updates
socket.on('queue_update', (data) => {
  updateQueueDisplay(data);
});

socket.on('ticket_called', (ticketNumber) => {
  showNotification(`Ticket ${ticketNumber} được gọi!`);
});
```

---

## 🟡 Intermediate Level

### Q6: Giải thích workflow hoàn chỉnh khi user đăng nhập vào hệ thống.

**💡 Đáp án:**

**Frontend Flow:**
1. User nhập email/password vào Login component
2. Form validation (react-hook-form)
3. Call `login()` function từ AuthContext
4. Axios POST request đến `/api/v1/auth/login`

**Backend Flow:**
5. FastAPI nhận request tại auth router
6. Validate credentials với database (SQLAlchemy)
7. Password verification với bcrypt hashing
8. Generate JWT token với user info
9. Return token + user data

**Frontend Response Handling:**
10. AuthContext nhận response
11. Store token trong localStorage
12. Update global auth state via useReducer
13. Navigate user đến appropriate dashboard based on role

**Code Example:**
```javascript
// AuthContext.js
const login = async (credentials) => {
  dispatch({ type: 'SET_LOADING', payload: true });
  
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    dispatch({ type: 'LOGIN_SUCCESS', payload: data.user });
  }
};
```

---

### Q7: Làm thế nào để implement role-based access control trong ứng dụng này?

**💡 Đáp án:**

**1. Backend Authorization:**
```python
# dependencies.py
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user = get_user_by_id(payload.get("sub"))
    return user

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# Route protection
@router.get("/admin-only")
def admin_endpoint(user: User = Depends(require_role("admin"))):
    return {"message": "Admin access granted"}
```

**2. Frontend Route Protection:**
```javascript
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return children;
};

// Usage
<Route path="/admin" element={
  <ProtectedRoute allowedRoles={['admin']}>
    <AdminDashboard />
  </ProtectedRoute>
} />
```

**3. Conditional UI Rendering:**
```javascript
const { user } = useAuth();

return (
  <div>
    {user.role === 'admin' && <AdminPanel />}
    {['manager', 'admin'].includes(user.role) && <ManagerFeatures />}
    <RegularUserContent />
  </div>
);
```

---

### Q8: Real-time queue updates được implement như thế nào? Mô tả flow chi tiết.

**💡 Đáp án:**

**Architecture:**
```
Staff Dashboard → Call Ticket → Backend → Redis → WebSocket Manager → Broadcast
                                                           ↓
                              Public Display ← ← ← All Connected Clients
```

**1. WebSocket Connection Setup:**
```javascript
// WebSocketContext.js
const WebSocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  
  useEffect(() => {
    const newSocket = io('ws://localhost:8000');
    newSocket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });
    
    newSocket.on('queue_update', handleQueueUpdate);
    newSocket.on('ticket_called', handleTicketCalled);
    
    setSocket(newSocket);
    return () => newSocket.close();
  }, []);
};
```

**2. Backend WebSocket Manager:**
```python
class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))
    
    async def send_to_client(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(json.dumps(message))
```

**3. Event Broadcasting:**
```python
# tickets.py
@router.post("/tickets/{ticket_id}/call")
async def call_ticket(ticket_id: int):
    ticket = update_ticket_status(ticket_id, "called")
    
    # Broadcast to all connected clients
    await websocket_manager.broadcast({
        "type": "ticket_called",
        "ticket_id": ticket_id,
        "ticket_number": ticket.number,
        "service": ticket.service.name
    })
    
    # Update queue display
    await websocket_manager.broadcast({
        "type": "queue_update",
        "queue_data": get_current_queue_status()
    })
```

---

### Q9: Tại sao sử dụng Redis trong dự án này? Các use cases cụ thể?

**💡 Đáp án:**

**Redis Use Cases trong dự án:**

**1. Session Storage cho WebSocket:**
```python
# Store WebSocket client sessions
await redis_client.hset(
    f"ws_session:{client_id}",
    mapping={
        "connected_at": datetime.now().isoformat(),
        "user_id": user.id if user else None,
        "session_type": "public_display"  # or "staff", "customer"
    }
)
```

**2. Queue State Caching:**
```python
# Cache current queue status
queue_data = {
    "current_number": "A001",
    "waiting_tickets": 15,
    "average_wait_time": "10 minutes"
}
await redis_client.setex("current_queue_status", 300, json.dumps(queue_data))
```

**3. Rate Limiting:**
```python
# Prevent API abuse
async def rate_limit_check(user_id: str):
    key = f"rate_limit:{user_id}"
    current = await redis_client.get(key)
    if current and int(current) > 100:  # 100 requests per hour
        raise HTTPException(429, "Rate limit exceeded")
    await redis_client.incr(key)
    await redis_client.expire(key, 3600)
```

**4. Pub/Sub for Microservices:**
```python
# Publish events to other services
await redis_client.publish("queue_events", json.dumps({
    "event": "ticket_created",
    "ticket_id": ticket.id,
    "timestamp": datetime.now().isoformat()
}))
```

**Lợi ích:**
- **Performance:** In-memory storage → sub-millisecond latency
- **Scalability:** Support multiple backend instances
- **Persistence:** Optional data persistence
- **Data Structures:** Lists, sets, sorted sets, hashes

---

### Q10: Docker Compose networking hoạt động như thế nào trong dự án?

**💡 Đáp án:**

**Network Architecture (Thực tế - Không có nginx):**
```yaml
networks:
  queue-network:
    driver: bridge
```

**Service Communication:**
```yaml
services:
  frontend:
    ports: ["3000:3000"]  # Direct exposure cho development
    networks: [queue-network]
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1  # Direct backend access
    
  backend:
    ports: ["8000:8000"]  # Direct exposure, no reverse proxy
    networks: [queue-network]
    environment:
      - DATABASE_URL=postgresql://admin:password@db:5432/queue_managment
      - REDIS_URL=redis://redis:6379
      - CORS_ORIGINS=http://localhost:3000  # Allow frontend access
    
  db:
    ports: ["5433:5432"]  # External port 5433 maps to internal 5432
    networks: [queue-network]
    
  redis:
    ports: ["6379:6379"]  # Direct Redis access
    networks: [queue-network]
```

**Internal DNS Resolution:**
- Container name = hostname trong network
- `backend` container connect đến `db:5432` (internal port)
- `frontend` gọi API qua external `localhost:8000` (not through container network)
- Redis accessible via `redis:6379`

**Development vs Production:**
```
Development (Current):
User → Frontend:3000 → Backend:8000 → Database:5432
                    → Redis:6379

Production (Would need):
User → Nginx:80 → Frontend (static) 
              → Backend:8000 → Database:5432
                           → Redis:6379
```

**Key Differences từ typical setup:**
- **No nginx reverse proxy** trong development
- **Direct port exposure** cho all services
- **CORS configuration** cần thiết vì cross-origin requests
- **Hot reload support** với volume mounting

---

## 🔴 Advanced Level

### Q11: Phân tích performance bottlenecks có thể xảy ra và cách optimize.

**💡 Đáp án:**

**1. Frontend Performance Issues:**

**Problem:** Re-rendering toàn bộ component tree khi Context state thay đổi
```javascript
// ❌ Bad: Single large context
const AppContext = createContext({
  user, tickets, queue, notifications, settings
});

// ✅ Good: Separate contexts
const AuthContext = createContext({ user });
const QueueContext = createContext({ tickets, queue });
const NotificationContext = createContext({ notifications });
```

**Solution:** 
- Sử dụng `React.memo()` và `useMemo()`
- Code splitting với `React.lazy()`
- Virtual scrolling cho large lists

**2. Backend Performance:**

**Problem:** N+1 Query problem với SQLAlchemy
```python
# ❌ Bad: N+1 queries
tickets = session.query(Ticket).all()
for ticket in tickets:
    print(ticket.user.name)  # Triggers separate query for each ticket

# ✅ Good: Eager loading
tickets = session.query(Ticket).options(joinedload(Ticket.user)).all()
```

**3. Database Optimization:**
```sql
-- Add indexes for frequent queries
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_service_id ON tickets(service_id);

-- Composite index for complex queries
CREATE INDEX idx_tickets_status_service ON tickets(status, service_id);
```

**4. Redis Caching Strategy:**
```python
async def get_queue_statistics():
    cache_key = "queue_stats"
    cached = await redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Expensive database query
    stats = calculate_queue_statistics()
    await redis_client.setex(cache_key, 60, json.dumps(stats))  # Cache 1 minute
    return stats
```

**5. WebSocket Optimization:**
```python
class OptimizedWebSocketManager:
    def __init__(self):
        self.connections = {}
        self.rooms = {}  # Group connections by type
    
    async def join_room(self, client_id: str, room: str):
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(client_id)
    
    async def broadcast_to_room(self, room: str, message: dict):
        # Only send to relevant clients
        if room in self.rooms:
            for client_id in self.rooms[room]:
                await self.send_to_client(client_id, message)
```

---

### Q12: Implement comprehensive error handling và logging strategy.

**💡 Đáp án:**

**1. Structured Logging với Correlation ID:**
```python
import structlog
import uuid
from fastapi import Request

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Middleware để add correlation ID
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    # Bind correlation ID to logger
    logger = structlog.get_logger().bind(correlation_id=correlation_id)
    request.state.logger = logger
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

**2. Global Exception Handler:**
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger = getattr(request.state, 'logger', structlog.get_logger())
    correlation_id = getattr(request.state, 'correlation_id', 'unknown')
    
    logger.error(
        "Unhandled exception",
        exception_type=type(exc).__name__,
        exception_message=str(exc),
        path=request.url.path,
        method=request.method,
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "correlation_id": correlation_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger = getattr(request.state, 'logger', structlog.get_logger())
    
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )
```

**3. Frontend Error Boundary:**
```javascript
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    this.logErrorToService(error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  logErrorToService = (error, errorInfo) => {
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };
    
    // Send to logging service
    fetch('/api/v1/errors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(errorReport)
    });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error && this.state.error.toString()}</pre>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}
```

**4. Circuit Breaker Pattern:**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise e
    
    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

# Usage
db_circuit_breaker = CircuitBreaker()

async def get_tickets():
    return await db_circuit_breaker.call(db_query_tickets)
```

---

### Q13: Design một caching strategy toàn diện cho hệ thống.

**💡 Đáp án:**

**Multi-Level Caching Architecture:**

**1. Browser Cache (Frontend):**
```javascript
// Service Worker for caching static assets
// sw.js
const CACHE_NAME = 'queue-management-v1';
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// React Query for API caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// Component usage
const { data: tickets, isLoading } = useQuery(
  ['tickets', filters],
  () => fetchTickets(filters),
  {
    staleTime: 30000, // 30 seconds for real-time data
  }
);
```

**2. Application Level Cache (Backend):**
```python
import asyncio
from functools import wraps
from typing import Any, Callable, Optional

class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.local_cache = {}  # In-memory cache for ultra-fast access
    
    async def get(self, key: str) -> Optional[Any]:
        # Try local cache first
        if key in self.local_cache:
            return self.local_cache[key]
        
        # Try Redis cache
        cached = await self.redis.get(key)
        if cached:
            data = json.loads(cached)
            self.local_cache[key] = data  # Store in local cache
            return data
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        serialized = json.dumps(value, default=str)
        await self.redis.setex(key, ttl, serialized)
        self.local_cache[key] = value
    
    async def invalidate(self, pattern: str):
        # Invalidate Redis cache
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
        
        # Invalidate local cache
        to_remove = [k for k in self.local_cache.keys() if pattern in k]
        for key in to_remove:
            del self.local_cache[key]

cache_manager = CacheManager(redis_client)

def cached(ttl: int = 300, key_prefix: str = ""):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

# Usage
@cached(ttl=60, key_prefix="queue")
async def get_queue_statistics(department_id: int):
    # Expensive database query
    return await db.execute(complex_query)
```

**3. Database Query Cache:**
```python
class DatabaseCacheStrategy:
    def __init__(self):
        self.query_cache = {}
    
    async def get_tickets_with_cache(
        self, 
        filters: dict,
        use_cache: bool = True
    ):
        cache_key = f"tickets:{hash(str(filters))}"
        
        if use_cache:
            cached = await cache_manager.get(cache_key)
            if cached:
                return cached
        
        # Database query with optimized joins
        query = (
            select(Ticket)
            .options(
                joinedload(Ticket.user),
                joinedload(Ticket.service),
                joinedload(Ticket.department)
            )
            .filter_by(**filters)
        )
        
        result = await db.execute(query)
        tickets = result.scalars().all()
        
        # Cache for 2 minutes (real-time data)
        await cache_manager.set(cache_key, tickets, ttl=120)
        return tickets
```

**4. Cache Invalidation Strategy:**
```python
class CacheInvalidationManager:
    def __init__(self, cache_manager):
        self.cache = cache_manager
        
    async def invalidate_ticket_cache(self, ticket_id: int):
        patterns = [
            f"tickets:*",
            f"queue:*",
            f"statistics:*",
            f"ticket:{ticket_id}:*"
        ]
        
        for pattern in patterns:
            await self.cache.invalidate(pattern)
    
    async def invalidate_user_cache(self, user_id: int):
        await self.cache.invalidate(f"user:{user_id}:*")
    
    async def on_ticket_created(self, ticket: Ticket):
        await self.invalidate_ticket_cache(ticket.id)
        # Invalidate related caches
        await self.cache.invalidate(f"queue:{ticket.service_id}:*")
        await self.cache.invalidate("statistics:*")

# Event-driven cache invalidation
@app.on_event("startup")
async def setup_cache_invalidation():
    # Redis pub/sub for cache invalidation across instances
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("cache_invalidation")
    
    async def handle_cache_invalidation():
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                await cache_manager.invalidate(data['pattern'])
    
    asyncio.create_task(handle_cache_invalidation())
```

**5. Cache Warming Strategy:**
```python
async def warm_cache():
    """Pre-populate cache with frequently accessed data"""
    
    # Warm up department data
    departments = await get_all_departments()
    await cache_manager.set("departments:all", departments, ttl=3600)
    
    # Warm up service data
    services = await get_all_services()
    await cache_manager.set("services:all", services, ttl=3600)
    
    # Warm up queue statistics
    for dept_id in [dept.id for dept in departments]:
        stats = await get_queue_statistics(dept_id)
        await cache_manager.set(f"queue:stats:{dept_id}", stats, ttl=300)

@app.on_event("startup")
async def startup_cache_warming():
    asyncio.create_task(warm_cache())
    
    # Schedule periodic cache warming
    async def periodic_cache_warming():
        while True:
            await asyncio.sleep(1800)  # Every 30 minutes
            await warm_cache()
    
    asyncio.create_task(periodic_cache_warming())
```

---

### Q14: Implement monitoring, alerting và observability cho production environment.

**💡 Đáp án:**

**1. Metrics Collection với Prometheus:**
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'websocket_active_connections',
    'Number of active WebSocket connections'
)

QUEUE_SIZE = Gauge(
    'queue_size_total',
    'Current queue size',
    ['department', 'service']
)

# Middleware for automatic metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# WebSocket metrics
class MetricsWebSocketManager(WebSocketManager):
    async def connect(self, websocket: WebSocket, client_id: str):
        success = await super().connect(websocket, client_id)
        if success:
            ACTIVE_CONNECTIONS.inc()
        return success
    
    def disconnect(self, client_id: str):
        super().disconnect(client_id)
        ACTIVE_CONNECTIONS.dec()

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")
```

**2. Health Checks:**
```python
from fastapi import status

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    checks = {
        "database": await check_database_health(),
        "redis": await check_redis_health(),
        "external_apis": await check_external_apis(),
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "version": "1.0.0"
    }

async def check_database_health() -> bool:
    try:
        await db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

async def check_redis_health() -> bool:
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False

@app.get("/health/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@app.get("/health/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    if await check_database_health() and await check_redis_health():
        return {"status": "ready"}
    raise HTTPException(503, "Service not ready")
```

**3. Distributed Tracing với OpenTelemetry:**
```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

# Setup tracing
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

# Auto-instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine)
RedisInstrumentor().instrument()

# Manual tracing for business logic
async def create_ticket_with_tracing(ticket_data: dict):
    with tracer.start_as_current_span("create_ticket") as span:
        span.set_attribute("ticket.service_id", ticket_data["service_id"])
        span.set_attribute("ticket.user_id", ticket_data["user_id"])
        
        try:
            # Database operation
            with tracer.start_as_current_span("db.create_ticket"):
                ticket = await create_ticket_in_db(ticket_data)
            
            # Cache operation
            with tracer.start_as_current_span("cache.invalidate"):
                await invalidate_ticket_cache()
            
            # WebSocket notification
            with tracer.start_as_current_span("websocket.broadcast"):
                await broadcast_ticket_created(ticket)
            
            span.set_attribute("ticket.id", ticket.id)
            span.set_status(trace.Status(trace.StatusCode.OK))
            return ticket
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            raise
```

**4. Alerting với Alert Manager:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'queue-management-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'queue-management-frontend'
    static_configs:
      - targets: ['frontend:3000']

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

# alert_rules.yml
groups:
  - name: queue_management_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: DatabaseConnectionDown
        expr: up{job="queue-management-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection is down"

      - alert: QueueTooLong
        expr: queue_size_total > 50
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Queue is getting too long"
          description: "Queue size is {{ $value }}"

      - alert: WebSocketConnectionDrop
        expr: rate(websocket_active_connections[5m]) < -10
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "WebSocket connections dropping rapidly"
```

**5. Log Aggregation với ELK Stack:**
```python
import logging
from pythonjsonlogger import jsonlogger

# Structured JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Business metrics logging
class BusinessMetricsLogger:
    def __init__(self):
        self.logger = logging.getLogger("business_metrics")
    
    def log_ticket_created(self, ticket):
        self.logger.info(
            "Ticket created",
            extra={
                "event_type": "ticket_created",
                "ticket_id": ticket.id,
                "service_id": ticket.service_id,
                "department_id": ticket.department_id,
                "wait_time_estimate": ticket.estimated_wait_time,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_ticket_called(self, ticket):
        actual_wait_time = (datetime.utcnow() - ticket.created_at).total_seconds()
        self.logger.info(
            "Ticket called",
            extra={
                "event_type": "ticket_called",
                "ticket_id": ticket.id,
                "actual_wait_time": actual_wait_time,
                "estimated_wait_time": ticket.estimated_wait_time,
                "wait_time_accuracy": abs(actual_wait_time - ticket.estimated_wait_time)
            }
        )

# Usage in business logic
business_logger = BusinessMetricsLogger()

async def call_ticket(ticket_id: int):
    ticket = await get_ticket(ticket_id)
    await update_ticket_status(ticket_id, "called")
    business_logger.log_ticket_called(ticket)
    await broadcast_ticket_called(ticket)
```

---

### Q15: Security hardening cho production deployment.

**💡 Đáp án:**

**1. Authentication & Authorization Security:**
```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import secrets

# Secure password hashing
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"], 
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,        # 3 iterations
    argon2__parallelism=4       # 4 threads
)

# JWT Security
class JWTManager:
    def __init__(self):
        self.SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),  # JWT ID for revocation
            "type": "access"
        })
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
    
    def create_refresh_token(self, user_id: int):
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),
            "type": "refresh"
        }
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

# Token blacklist for logout
class TokenBlacklist:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def revoke_token(self, jti: str, exp: datetime):
        # Store until expiration
        ttl = int((exp - datetime.utcnow()).total_seconds())
        await self.redis.setex(f"blacklist:{jti}", ttl, "1")
    
    async def is_revoked(self, jti: str) -> bool:
        return await self.redis.exists(f"blacklist:{jti}")

# Rate limiting
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        current = await self.redis.get(key)
        if current is None:
            await self.redis.setex(key, window, 1)
            return True
        
        if int(current) >= limit:
            return False
        
        await self.redis.incr(key)
        return True

# Usage
rate_limiter = RateLimiter(redis_client)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    if not await rate_limiter.is_allowed(key, limit=100, window=60):
        raise HTTPException(429, "Rate limit exceeded")
    
    return await call_next(request)
```

**2. Input Validation & Sanitization:**
```python
from pydantic import BaseModel, validator, Field
from typing import Optional
import bleach
import re

class SecureTicketCreate(BaseModel):
    service_id: int = Field(..., gt=0, description="Service ID must be positive")
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: Optional[str] = Field(None, regex=r'^\+?[1-9]\d{1,14}$')
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('customer_name')
    def sanitize_name(cls, v):
        # Remove HTML tags and dangerous characters
        cleaned = bleach.clean(v, tags=[], strip=True)
        # Only allow letters, spaces, and common punctuation
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\-\.\']+$', cleaned):
            raise ValueError('Name contains invalid characters')
        return cleaned.strip()
    
    @validator('notes')
    def sanitize_notes(cls, v):
        if v:
            # Allow basic formatting but remove scripts
            allowed_tags = ['p', 'br', 'strong', 'em']
            return bleach.clean(v, tags=allowed_tags, strip=True)
        return v

# SQL Injection Prevention
class SecureDatabase:
    def __init__(self, engine):
        self.engine = engine
    
    async def execute_query(self, query: str, params: dict = None):
        # Always use parameterized queries
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(query), params or {})
                return result
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise HTTPException(500, "Database operation failed")

# Example usage
async def get_tickets_secure(
    department_id: int,
    status: Optional[str] = None,
    limit: int = 50
):
    # Validate inputs
    if limit > 100:
        raise HTTPException(400, "Limit cannot exceed 100")
    
    # Use parameterized query
    query = """
        SELECT * FROM tickets 
        WHERE department_id = :dept_id
        AND (:status IS NULL OR status = :status)
        ORDER BY created_at DESC
        LIMIT :limit
    """
    
    return await secure_db.execute_query(query, {
        "dept_id": department_id,
        "status": status,
        "limit": limit
    })
```

**3. HTTPS & Security Headers:**
```python
from fastapi.security import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Force HTTPS in production
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "connect-src 'self' ws: wss:;"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response
```

**4. Docker Security:**
```dockerfile
# Secure Dockerfile
FROM python:3.11-slim-bullseye

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Remove sensitive files
RUN rm -rf .git .env.example tests/

# Set permissions
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml security
version: '3.8'
services:
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - REDIS_URL=${REDIS_URL}
    secrets:
      - db_password
      - jwt_secret
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp
      - /var/run

secrets:
  db_password:
    external: true
  jwt_secret:
    external: true

networks:
  default:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.enable_icc: "false"
```

**5. Secrets Management:**
```python
import os
from cryptography.fernet import Fernet

class SecretsManager:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        self.cipher_suite = Fernet(self.key)
    
    def encrypt_secret(self, secret: str) -> str:
        return self.cipher_suite.encrypt(secret.encode()).decode()
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        return self.cipher_suite.decrypt(encrypted_secret.encode()).decode()
    
    def get_secret(self, key: str) -> str:
        # Try environment variable first
        value = os.getenv(key)
        if value:
            return value
        
        # Try encrypted secrets store
        encrypted_value = os.getenv(f"{key}_ENCRYPTED")
        if encrypted_value:
            return self.decrypt_secret(encrypted_value)
        
        raise ValueError(f"Secret {key} not found")

# Usage
secrets = SecretsManager()
DATABASE_URL = secrets.get_secret("DATABASE_URL")
JWT_SECRET = secrets.get_secret("JWT_SECRET_KEY")
```

---

Tài liệu này cung cấp một cái nhìn toàn diện về Queue Management System từ cơ bản đến nâng cao, bao gồm các khái niệm, kiến trúc, implementation details, và best practices cho production environment.