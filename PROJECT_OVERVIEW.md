# 📋 Queue Management System - Tổng Quan Dự Án

## 🎯 Mục Đích
Hệ thống quản lý hàng đợi thông minh cho các cơ quan nhà nước, hỗ trợ quản lý khách hàng, đánh giá dịch vụ, và theo dõi hiệu suất nhân viên.

---

## 🏗️ Kiến Trúc Tổng Thể

### Tech Stack

**Backend:**
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL 15
- **Cache/Session:** Redis 7
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT (python-jose)
- **Real-time:** WebSocket (FastAPI native)

**Frontend:**
- **Framework:** React 18.2.0
- **Routing:** React Router DOM 6.8
- **State Management:** Context API + useReducer
- **Styling:** Tailwind CSS 3.2
- **Real-time:** WebSocket (native WebSocket API)
- **Forms:** React Hook Form 7.43
- **UI Components:** Lucide React icons, Custom components

**DevOps:**
- **Containerization:** Docker + Docker Compose
- **Database:** PostgreSQL container
- **Cache:** Redis container
- **Hot Reload:** Volume mounting for development

---

## 📁 Cấu Trúc Thư Mục

```
queue-management-system/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API routes version 1
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── tickets.py     # Ticket management
│   │   │   ├── services.py    # Service endpoints
│   │   │   ├── departments.py # Department endpoints
│   │   │   ├── dashboard.py   # Dashboard data
│   │   │   ├── feedback.py    # Feedback & reviews
│   │   │   └── roles/         # Role-specific routes
│   │   │       ├── staff.py   # Staff operations
│   │   │       └── manager.py # Manager operations
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Settings & environment
│   │   │   ├── database.py    # DB connection & setup
│   │   │   └── security.py    # JWT & password hashing
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py        # User model
│   │   │   ├── ticket.py      # QueueTicket model
│   │   │   ├── service.py     # Service model
│   │   │   ├── department.py  # Department model
│   │   │   ├── feedback.py    # Feedback model
│   │   │   └── ...
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic layer
│   │   ├── websocket_manager.py # WebSocket connection manager
│   │   └── main.py            # FastAPI app entry point
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Backend container config
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── features/          # Feature-based modules
│   │   │   ├── auth/          # Authentication
│   │   │   │   └── components/Login.js
│   │   │   ├── dashboard/     # Dashboard pages
│   │   │   │   ├── pages/
│   │   │   │   │   ├── AdminDashboard.js
│   │   │   │   │   ├── ManagerDashboard.js
│   │   │   │   │   └── StaffDashboard.js
│   │   │   ├── queue/         # Queue management
│   │   │   │   └── pages/
│   │   │   │       ├── ServiceRegistration.js
│   │   │   │       ├── WaitingPage.js
│   │   │   │       ├── PublicDisplay.js
│   │   │   │       └── FeedbackPage.js
│   │   │   └── schedule/      # Schedule management
│   │   ├── shared/            # Shared components & utilities
│   │   │   ├── AuthContext.js      # Authentication context
│   │   │   ├── WebSocketContext.js # WebSocket context
│   │   │   ├── api.js              # API client
│   │   │   └── components/         # Reusable components
│   │   ├── routes/
│   │   │   └── AppRoutes.js   # Route configuration
│   │   ├── App.js             # Main app component
│   │   └── index.js           # React entry point
│   ├── package.json           # Node dependencies
│   └── Dockerfile             # Frontend container config
│
├── database/                  # Database scripts
│   ├── schema.sql            # Database schema (tables, types)
│   ├── data.sql              # Sample data
│   ├── setup_complete.sql    # Complete setup script
│   └── migration_ticket_complaints.sql
│
├── docker-compose.yml        # Multi-container orchestration
└── openapi.json             # API documentation (OpenAPI 3.1)
```

---

## 🗄️ Cơ Sở Dữ Liệu

### Các Bảng Chính

**1. departments** - Phòng ban
- `id`, `name`, `description`, `code`
- `qr_code_token` - Token cho QR code đăng ký
- `max_concurrent_customers` - Số khách tối đa
- `operating_hours` - Giờ làm việc (JSONB)

**2. users** - Người dùng (Admin, Manager, Staff)
- `id`, `username`, `email`, `password_hash`
- `role` - Enum: 'admin', 'manager', 'staff'
- `department_id` - Phòng ban làm việc
- `is_active`, `last_login`

**3. services** - Dịch vụ
- `id`, `name`, `description`, `service_code`
- `department_id` - Thuộc phòng ban nào
- `estimated_duration` - Thời gian ước tính (phút)
- `form_schema` - Cấu hình form động (JSONB)

**4. queue_tickets** - Vé hàng đợi ⭐
- `id`, `ticket_number` - Số vé (A001, B002, ...)
- `customer_name`, `customer_phone`, `customer_email`
- `service_id`, `department_id`, `staff_id`
- `status` - Enum: 'waiting', 'called', 'completed', 'no_show'
- `priority` - Enum: 'normal', 'high', 'elderly', 'disabled', 'vip'
- `queue_position` - Vị trí trong hàng đợi
- `form_data` - Dữ liệu form khách hàng điền (JSONB)
- Timestamps: `created_at`, `called_at`, `served_at`, `completed_at`

**5. Hệ Thống Đánh Giá (Integrated vào queue_tickets):**
- `service_rating` - Đánh giá dịch vụ (1-5 ⭐)
- `staff_rating` - Đánh giá nhân viên (1-5 ⭐)
- `speed_rating` - Đánh giá tốc độ (1-5 ⭐)
- `overall_rating` - Đánh giá tổng thể (1-5 ⭐)
- `review_comments` - Bình luận chi tiết
- `reviewed_at` - Thời gian đánh giá

**6. staff_performance** - Hiệu suất nhân viên
- `user_id`, `department_id`, `date`
- `tickets_served` - Số vé đã xử lý
- `avg_service_time` - Thời gian phục vụ trung bình
- `avg_rating` - Đánh giá trung bình từ khách hàng

**7. feedback** - Phản hồi tổng quát (riêng biệt với review)
- `ticket_id`, `customer_name`, `rating`, `message`
- `category`, `is_anonymous`

**8. ticket_complaints** - Khiếu nại
- `ticket_id`, `complaint_text`, `status`
- `assigned_to` - Manager xử lý
- `manager_response`

**9. staff_notifications** - Thông báo cho nhân viên
- `recipient_id`, `title`, `message`
- `notification_type` - 'complaint', 'announcement', 'alert'
- `is_read`, `is_archived`
- `complaint_details` - JSONB chứa thông tin khiếu nại

**10. Các Bảng Hỗ Trợ:**
- `counters` - Quầy phục vụ
- `service_sessions` - Phiên phục vụ
- `qr_codes` - QR codes cho đăng ký di động
- `announcements` - Thông báo hệ thống
- `activity_logs` - Nhật ký hoạt động

### Enum Types

- `user_role`: 'admin', 'manager', 'staff'
- `ticket_status`: 'waiting', 'called', 'completed', 'no_show'
- `ticket_priority`: 'normal', 'high', 'elderly', 'disabled', 'vip'
- `field_type`: 'text', 'email', 'phone', 'textarea', 'select', 'checkbox', 'radio', 'number', 'date'
- `session_status`: 'active', 'paused', 'completed', 'cancelled'

---

## 🔐 Xác Thực & Phân Quyền

### Role-Based Access Control (RBAC)

**Admin:**
- Quản lý toàn bộ hệ thống
- Xem tất cả dashboard
- Quản lý departments, services, users

**Manager:**
- Quản lý phòng ban của mình
- Xem báo cáo hiệu suất
- Xử lý khiếu nại
- Quản lý staff trong phòng ban

**Staff:**
- Xử lý tickets
- Gọi số thứ tự
- Hoàn thành dịch vụ
- Xem dashboard của mình

### Authentication Flow

1. User đăng nhập với `email` + `password`
2. Backend verify credentials với database
3. Tạo JWT token (expire: 24 giờ)
4. Frontend lưu token vào `localStorage`
5. Mỗi request gửi kèm header: `Authorization: Bearer <token>`
6. Backend verify token và trích xuất user info

---

## 📡 API Endpoints Chính

### Authentication
- `POST /api/v1/auth/login` - Đăng nhập

### Departments
- `GET /api/v1/departments` - Danh sách phòng ban
- `GET /api/v1/departments/{id}` - Chi tiết phòng ban

### Services
- `GET /api/v1/services?department_id={id}` - Dịch vụ theo phòng ban

### Tickets
- `POST /api/v1/tickets/register` - Đăng ký vé hàng đợi (public)
- `POST /api/v1/tickets` - Tạo vé (authenticated)
- `GET /api/v1/tickets/{id}/status` - Xem trạng thái vé (public)
- `POST /api/v1/tickets/{id}/cancel` - Hủy vé (public)
- `GET /api/v1/tickets/{id}` - Chi tiết vé (authenticated)

### Staff Operations
- `GET /api/v1/staff/tickets` - Danh sách vé của staff
- `POST /api/v1/staff/tickets/{id}/call` - Gọi số thứ tự
- `POST /api/v1/staff/tickets/{id}/complete` - Hoàn thành dịch vụ

### Manager Operations
- `GET /api/v1/manager/dashboard` - Dashboard quản lý
- `GET /api/v1/manager/performance` - Báo cáo hiệu suất
- `POST /api/v1/manager/complaints/{id}/respond` - Phản hồi khiếu nại

### Feedback & Reviews
- `POST /api/v1/feedback` - Gửi phản hồi
- `POST /api/v1/tickets/{id}/review` - Đánh giá vé đã hoàn thành

### WebSocket
- `WS /ws/{client_id}` - Kết nối WebSocket cho real-time updates

---

## 🔄 Quy Trình Hoạt Động

### 1. Khách Hàng Đăng Ký Dịch vụ

1. Truy cập trang `/service-registration`
2. Chọn phòng ban → Chọn dịch vụ
3. Điền form động (theo `form_schema` của service)
4. Gửi yêu cầu → Backend tạo ticket
5. Nhận `ticket_number` (VD: A001)
6. Chuyển đến `/waiting/{ticketId}` để theo dõi

### 2. Staff Xử Lý Ticket

1. Staff đăng nhập → Dashboard `/staff`
2. Xem danh sách tickets đang chờ
3. Click "Call" → Ticket status → 'called'
4. WebSocket broadcast → Khách hàng nhận thông báo
5. Phục vụ khách hàng
6. Click "Complete" → Ticket status → 'completed'

### 3. Khách Hàng Đánh Giá

1. Sau khi ticket completed, chuyển đến `/review/{ticketId}`
2. Đánh giá 4 tiêu chí: Service, Staff, Speed, Overall (1-5 ⭐)
3. Viết bình luận (tùy chọn)
4. Gửi review → Lưu vào `queue_tickets`
5. Cập nhật `staff_performance` với rating mới

### 4. Real-time Updates (WebSocket)

**Khi có sự kiện:**
- Ticket mới được tạo → Broadcast đến staff dashboard
- Ticket được gọi → Broadcast đến khách hàng đang chờ
- Queue position thay đổi → Update WaitingPage
- Ticket completed → Notify khách hàng

**WebSocket Message Types:**
```json
{
  "type": "queue_update",
  "ticket_id": "123",
  "data": { ... }
}
```

---

## 🚀 Khởi Động Dự Án

### Development Mode (Docker Compose)

```bash
# 1. Khởi động tất cả services
docker-compose up -d

# 2. Services sẽ chạy trên:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - Database: localhost:5433
# - Redis: localhost:6379

# 3. Xem logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Database Setup

```bash
# Kết nối PostgreSQL
psql -h localhost -p 5433 -U admin -d queue_managment

# Hoặc chạy setup script
psql -h localhost -p 5433 -U admin -d queue_managment -f database/setup_complete.sql
```

### Credentials Mặc Định

**Admin:**
- Email: `admin@qstream.vn`
- Password: `Admin123!`

**Manager:**
- Email: `manager.01@qstream.vn`
- Password: `Admin123!`

**Staff:**
- Email: `staff.01@qstream.vn`
- Password: `Admin123!`

---

## 📊 Tính Năng Chính

### ✅ Đã Triển Khai

1. **Quản Lý Hàng Đợi**
   - Tạo ticket với auto-assign staff
   - Ưu tiên (priority levels)
   - Vị trí trong hàng đợi
   - Ước tính thời gian chờ

2. **Hệ Thống Đánh Giá**
   - 4 tiêu chí đánh giá (1-5 sao)
   - Bình luận chi tiết
   - Tích hợp với performance tracking

3. **Real-time Updates**
   - WebSocket cho live notifications
   - Queue status updates
   - Ticket call notifications

4. **Dashboard Theo Role**
   - Admin: Toàn bộ hệ thống
   - Manager: Quản lý phòng ban
   - Staff: Xử lý tickets

5. **Mobile Registration**
   - QR code generation
   - Mobile-friendly forms

6. **Performance Tracking**
   - Số vé đã xử lý
   - Đánh giá trung bình
   - Thời gian phục vụ trung bình

### 🔄 Có Thể Mở Rộng

1. SMS/Email notifications
2. Multi-language support
3. Advanced analytics & reports
4. Mobile app (React Native)
5. Appointment scheduling
6. Video queue (remote service)

---

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=postgresql://admin:password@db:5432/queue_managment
REDIS_URL=redis://redis:6379
SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
```

---

## 📝 Ghi Chú Quan Trọng

1. **Database Schema:** Đã được tối ưu với indexes cho performance
2. **Security:** JWT tokens có expire time, password hashing với bcrypt
3. **WebSocket:** Connection pooling và reconnection logic
4. **Form Schema:** Dynamic forms dựa trên JSONB configuration
5. **Ticket Numbering:** Format A001, B002, C003... theo department

---

## 📚 Tài Liệu Tham Khảo

- **Mock Interview Guide:** `Đọc hiểu/mock_interview.md` - 15 câu hỏi từ Beginner đến Advanced
- **API Documentation:** `http://localhost:8000/docs` (Swagger UI khi chạy backend)
- **OpenAPI Spec:** `openapi.json`

---

## 🐛 Troubleshooting

### Common Issues

1. **Database connection failed**
   - Check docker-compose.yml database service
   - Verify DATABASE_URL in backend config

2. **CORS errors**
   - Update CORS_ORIGINS in backend config
   - Check browser console for exact error

3. **WebSocket connection failed**
   - Verify WS_URL in frontend config
   - Check backend WebSocket endpoint logs

4. **Ticket creation fails**
   - Check service_id và department_id exist
   - Verify form_data matches form_schema

---

**Version:** 1.0.0  
**Last Updated:** October 2025  
**Maintainer:** Development Team

