-- =====================================================
-- QUEUE MANAGEMENT SYSTEM - SAMPLE DATA
-- =====================================================
-- Created: October 22, 2025
-- Purpose: Sample data for development and testing
-- Usage: Run after schema.sql to populate database
-- Version: 3.0

-- =====================================================
-- DEPARTMENT DATA
-- =====================================================

-- Insert government departments with realistic Vietnamese names
INSERT INTO departments (name, description, code, max_concurrent_customers, operating_hours, is_active) VALUES
('Phòng Kế hoạch Tổng hợp', 'Quản lý kế hoạch và tổng hợp các hoạt động', 'KHTH', 30, 
 '{"open": "08:00", "close": "17:00", "lunch_break": {"start": "12:00", "end": "13:00"}}', TRUE),

('Phòng Tài chính Kế toán', 'Quản lý tài chính, ngân sách và kế toán', 'TCKT', 25, 
 '{"open": "08:00", "close": "17:00", "lunch_break": {"start": "12:00", "end": "13:00"}}', TRUE),

('Phòng Hành chính Quản trị', 'Quản lý hành chính, nhân sự và văn thư', 'HCQT', 20, 
 '{"open": "08:00", "close": "17:00", "lunch_break": {"start": "12:00", "end": "13:00"}}', TRUE),

('Phòng Công nghệ Thông tin', 'Quản lý hệ thống CNTT và dữ liệu điện tử', 'CNTT', 15, 
 '{"open": "08:00", "close": "17:00", "lunch_break": {"start": "12:00", "end": "13:00"}}', TRUE);

-- =====================================================
-- USER ACCOUNTS (Password: Admin123!)
-- =====================================================

-- Insert users with pre-hashed passwords for immediate login
INSERT INTO users (username, password_hash, email, phone, full_name, role, department_id) VALUES
-- System Administrator
('admin', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'admin@qstream.vn', '0123456789', 'Quản trị viên Hệ thống', 'admin', 1),

-- Department Managers
('manager.01', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'manager.01@qstream.vn', '0123456790', 'Nguyễn Văn Quản lý', 'manager', 1),

-- Staff Members
('staff.01', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'staff.01@qstream.vn', '0123456791', 'Trần Thị Nhân viên', 'staff', 1),

('staff.02', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'staff.02@qstream.vn', '0123456792', 'Lê Văn Phục vụ', 'staff', 2),

('staff.03', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'staff.03@qstream.vn', '0123456793', 'Phạm Thị Hỗ trợ', 'staff', 3),

('staff.04', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'staff.04@qstream.vn', '0123456794', 'Hoàng Văn Kỹ thuật', 'staff', 4);

-- =====================================================
-- SERVICES DATA
-- =====================================================

-- Insert services available in each department (4 services per department)
INSERT INTO services (name, description, department_id, service_code, estimated_duration, form_schema) VALUES
-- Department 1: Phòng Kế hoạch Tổng hợp (4 services)
('Đăng ký kinh doanh', 'Dịch vụ đăng ký giấy phép kinh doanh', 1, 'DKKD', 30, 
 '{"fields": [{"name": "business_name", "label": "Tên doanh nghiệp", "type": "text", "required": true}, {"name": "business_type", "label": "Loại hình kinh doanh", "type": "select", "required": true}]}'),
('Lập kế hoạch dự án', 'Hỗ trợ lập kế hoạch và quản lý dự án', 1, 'KHDA', 45, 
 '{"fields": [{"name": "project_name", "label": "Tên dự án", "type": "text", "required": true}, {"name": "duration", "label": "Thời gian thực hiện", "type": "number", "required": true}]}'),
('Báo cáo thống kê', 'Lập báo cáo và thống kê hoạt động', 1, 'BCTK', 30, 
 '{"fields": [{"name": "report_type", "label": "Loại báo cáo", "type": "select", "required": true}, {"name": "period", "label": "Kỳ báo cáo", "type": "select", "required": true}]}'),
('Tư vấn quy trình', 'Tư vấn về quy trình và thủ tục hành chính', 1, 'TVQT', 25, 
 '{"fields": [{"name": "process_type", "label": "Loại quy trình", "type": "select", "required": true}, {"name": "question", "label": "Câu hỏi tư vấn", "type": "textarea", "required": true}]}'),

-- Department 2: Phòng Tài chính Kế toán (4 services)  
('Nộp thuế', 'Dịch vụ nộp thuế và kê khai thuế', 2, 'NTHUE', 15, 
 '{"fields": [{"name": "tax_code", "label": "Mã số thuế", "type": "text", "required": true}, {"name": "tax_period", "label": "Kỳ nộp thuế", "type": "select", "required": true}]}'),
('Thanh toán hóa đơn', 'Xử lý thanh toán các loại hóa đơn', 2, 'TTHD', 20, 
 '{"fields": [{"name": "invoice_number", "label": "Số hóa đơn", "type": "text", "required": true}, {"name": "amount", "label": "Số tiền", "type": "number", "required": true}]}'),
('Kế toán doanh thu', 'Quản lý và kế toán doanh thu', 2, 'KTDT', 35, 
 '{"fields": [{"name": "revenue_type", "label": "Loại doanh thu", "type": "select", "required": true}, {"name": "amount", "label": "Số tiền", "type": "number", "required": true}]}'),
('Kiểm tra tài chính', 'Kiểm tra và đối soát tài chính', 2, 'KTTC', 40, 
 '{"fields": [{"name": "audit_type", "label": "Loại kiểm tra", "type": "select", "required": true}, {"name": "period", "label": "Kỳ kiểm tra", "type": "select", "required": true}]}'),

-- Department 3: Phòng Hành chính Quản trị (4 services)
('Cấp giấy tờ', 'Dịch vụ cấp các loại giấy tờ, chứng nhận', 3, 'CGTO', 20, 
 '{"fields": [{"name": "document_type", "label": "Loại giấy tờ", "type": "select", "required": true}, {"name": "urgent", "label": "Xử lý khẩn cấp", "type": "checkbox", "required": false}]}'),
('Cấp phép hoạt động', 'Cấp các loại giấy phép hoạt động', 3, 'CPHD', 50, 
 '{"fields": [{"name": "license_type", "label": "Loại giấy phép", "type": "select", "required": true}, {"name": "business_scope", "label": "Phạm vi hoạt động", "type": "textarea", "required": true}]}'),
('Quản lý nhân sự', 'Xử lý hồ sơ và quản lý nhân sự', 3, 'QLNS', 30, 
 '{"fields": [{"name": "employee_id", "label": "Mã nhân viên", "type": "text", "required": true}, {"name": "request_type", "label": "Loại yêu cầu", "type": "select", "required": true}]}'),
('Văn thư lưu trữ', 'Quản lý văn bản và lưu trữ hồ sơ', 3, 'VTLT', 15, 
 '{"fields": [{"name": "document_title", "label": "Tiêu đề văn bản", "type": "text", "required": true}, {"name": "storage_type", "label": "Loại lưu trữ", "type": "select", "required": true}]}'),

-- Department 4: Phòng Công nghệ Thông tin (4 services)
('Hỗ trợ kỹ thuật', 'Dịch vụ hỗ trợ kỹ thuật CNTT', 4, 'HTKT', 25, 
 '{"fields": [{"name": "issue_type", "label": "Loại vấn đề", "type": "select", "required": true}, {"name": "description", "label": "Mô tả chi tiết", "type": "textarea", "required": true}]}'),
('Cài đặt phần mềm', 'Hỗ trợ cài đặt và cấu hình phần mềm', 4, 'CDPM', 60, 
 '{"fields": [{"name": "software_name", "label": "Tên phần mềm", "type": "text", "required": true}, {"name": "version", "label": "Phiên bản", "type": "text", "required": false}]}'),
('Bảo trì hệ thống', 'Bảo trì và nâng cấp hệ thống IT', 4, 'BTHT', 90, 
 '{"fields": [{"name": "system_type", "label": "Loại hệ thống", "type": "select", "required": true}, {"name": "maintenance_type", "label": "Loại bảo trì", "type": "select", "required": true}]}'),
('Đào tạo CNTT', 'Đào tạo sử dụng công nghệ thông tin', 4, 'DTCN', 120, 
 '{"fields": [{"name": "course_name", "label": "Tên khóa học", "type": "text", "required": true}, {"name": "participants", "label": "Số lượng học viên", "type": "number", "required": true}]}');

-- =====================================================
-- COUNTER DATA
-- =====================================================

-- Insert service counters for each department (1 counter per department)
INSERT INTO counters (name, number, department_id, assigned_staff_id) VALUES
('Quầy số 1', 1, 1, 3),  -- Phòng Kế hoạch Tổng hợp -> staff.01
('Quầy số 2', 2, 2, 4),  -- Phòng Tài chính Kế toán -> staff.02  
('Quầy số 3', 3, 3, 5),  -- Phòng Hành chính Quản trị -> staff.03
('Quầy số 4', 4, 4, 6);  -- Phòng Công nghệ Thông tin -> staff.04

-- =====================================================
-- SAMPLE QUEUE TICKETS WITH REVIEWS
-- =====================================================

-- Insert realistic queue tickets with various statuses and some with review data
INSERT INTO queue_tickets (
    ticket_number, customer_name, customer_phone, customer_email, 
    service_id, department_id, status, priority, queue_position,
    form_data, notes, created_at, completed_at,
    service_rating, staff_rating, speed_rating, overall_rating, 
    review_comments, reviewed_at
) VALUES

-- Completed ticket with excellent review
('A001', 'Nguyễn Văn A', '0987654321', 'nguyenvana@email.com', 1, 1, 'completed', 'normal', 1,
 '{"business_name": "Công ty ABC", "business_type": "Công ty TNHH"}', 
 'Khách hàng đã hoàn thành thủ tục đăng ký kinh doanh', 
 '2025-10-22 08:00:00', '2025-10-22 08:30:00',
 5, 5, 4, 5, 'Dịch vụ rất tốt, nhân viên nhiệt tình và chuyên nghiệp. Thủ tục nhanh gọn.', '2025-10-22 08:35:00'),

-- Completed ticket with good review
('B002', 'Trần Thị B', '0987654322', 'tranthib@email.com', 2, 2, 'completed', 'normal', 2,
 '{"tax_code": "123456789", "tax_period": "Quý 3/2025"}', 
 'Nộp thuế thành công, đã in biên lai', 
 '2025-10-22 08:15:00', '2025-10-22 08:30:00',
 4, 4, 5, 4, 'Xử lý nhanh chóng và chính xác. Nhân viên hướng dẫn tận tình.', '2025-10-22 08:32:00'),

-- Current waiting ticket (high priority)
('C003', 'Lê Văn C', '0987654323', 'levanc@email.com', 3, 3, 'waiting', 'high', 1,
 '{"document_type": "Giấy chứng nhận đăng ký cư trú", "urgent": true}', 
 'Ưu tiên xử lý - khách hàng có việc gấp', 
 '2025-10-22 09:00:00', NULL,
 NULL, NULL, NULL, NULL, NULL, NULL),

-- Currently being served
('D004', 'Phạm Thị D', '0987654324', 'phamthid@email.com', 1, 1, 'called', 'normal', 2,
 '{"business_name": "Cửa hàng XYZ", "business_type": "Hộ kinh doanh"}', 
 'Đang xử lý hồ sơ đăng ký kinh doanh', 
 '2025-10-22 09:15:00', NULL,
 NULL, NULL, NULL, NULL, NULL, NULL),

-- Completed ticket with mixed review
('E005', 'Hoàng Văn E', '0987654325', 'hoangvane@email.com', 4, 4, 'completed', 'normal', 1,
 '{"issue_type": "Lỗi phần mềm", "description": "Máy tính không thể kết nối mạng"}', 
 'Đã khắc phục sự cố kết nối mạng', 
 '2025-10-22 09:30:00', '2025-10-22 10:00:00',
 3, 4, 3, 3, 'Nhân viên kỹ thuật giỏi nhưng thời gian chờ hơi lâu. Có thể cải thiện tốc độ xử lý.', '2025-10-22 10:05:00');

-- =====================================================
-- FEEDBACK DATA
-- =====================================================

-- Insert additional feedback entries (separate from ticket reviews)
INSERT INTO feedback (ticket_id, customer_name, customer_email, rating, category, message, created_at) VALUES
(1, 'Nguyễn Văn A', 'nguyenvana@email.com', 5, 'service_quality', 
 'Rất hài lòng với dịch vụ! Nhân viên tận tình và quy trình rõ ràng.', '2025-10-22 08:35:00'),

(2, 'Trần Thị B', 'tranthib@email.com', 4, 'speed', 
 'Xử lý nhanh chóng, không phải chờ đợi lâu.', '2025-10-22 08:32:00'),

(5, 'Hoàng Văn E', 'hoangvane@email.com', 3, 'technical', 
 'Kỹ thuật viên giải quyết được vấn đề nhưng cần cải thiện thời gian phản hồi.', '2025-10-22 10:05:00');

-- =====================================================
-- STAFF PERFORMANCE DATA
-- =====================================================

-- Insert staff performance tracking data
INSERT INTO staff_performance (user_id, department_id, date, tickets_served, avg_service_time, total_rating_score, rating_count, avg_rating) VALUES
-- Staff1 performance (excellent)
(3, 1, '2025-10-22', 2, 25.5, 10, 2, 5.0),

-- Staff2 performance (good)
(4, 2, '2025-10-22', 1, 15.0, 4, 1, 4.0),

-- Staff3 performance (no tickets served today)
(5, 3, '2025-10-22', 0, 0, 0, 0, 0);

-- =====================================================
-- QR CODES DATA
-- =====================================================

-- Insert QR codes for mobile registration
INSERT INTO qr_codes (department_id, registration_url, expires_at) VALUES
(1, 'http://localhost:3000/register?dept=1&token=uuid1', '2025-12-31 23:59:59'),
(2, 'http://localhost:3000/register?dept=2&token=uuid2', '2025-12-31 23:59:59'),
(3, 'http://localhost:3000/register?dept=3&token=uuid3', '2025-12-31 23:59:59'),
(4, 'http://localhost:3000/register?dept=4&token=uuid4', '2025-12-31 23:59:59');

-- =====================================================
-- ANNOUNCEMENTS DATA
-- =====================================================

-- Insert system announcements
INSERT INTO announcements (title, content, type, target_audience, department_id, created_by, expires_at) VALUES
('Thông báo bảo trì hệ thống', 
 'Hệ thống sẽ được bảo trì từ 18:00-20:00 hôm nay để nâng cấp tính năng mới. Vui lòng hoàn tất các giao dịch trước thời gian này.', 
 'maintenance', 'all', NULL, 1, '2025-10-22 20:00:00'),

('Cập nhật quy trình đăng ký kinh doanh', 
 'Từ ngày 25/10/2025, quy trình đăng ký kinh doanh sẽ có một số thay đổi để đơn giản hóa thủ tục. Vui lòng tham khảo hướng dẫn mới.', 
 'general', 'staff', 1, 2, '2025-10-30 23:59:59');

-- =====================================================
-- SHIFT DEFINITIONS
-- =====================================================

-- Insert default shift definitions for schedule management
INSERT INTO shifts (id, name, shift_type, start_time, end_time, description, is_active) VALUES
(
    '550e8400-e29b-41d4-a716-446655440001'::uuid,
    'Ca Sáng',
    'morning',
    '07:00:00',
    '15:00:00',
    'Ca làm việc buổi sáng từ 7:00 đến 15:00',
    TRUE
),
(
    '550e8400-e29b-41d4-a716-446655440002'::uuid,
    'Ca Chiều',
    'afternoon',
    '15:00:00',
    '23:00:00',
    'Ca làm việc buổi chiều từ 15:00 đến 23:00',
    TRUE
),
(
    '550e8400-e29b-41d4-a716-446655440003'::uuid,
    'Ca Tối',
    'night',
    '23:00:00',
    '07:00:00',
    'Ca làm việc buổi tối từ 23:00 đến 7:00 (ngày hôm sau)',
    TRUE
);

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '✅ SAMPLE DATA INSERTED SUCCESSFULLY!';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE '👥 User Accounts Created (Password: Admin123!):';
    RAISE NOTICE '   - admin@qstream.vn (System Admin)';
    RAISE NOTICE '   - manager.01@qstream.vn (Department Manager)';  
    RAISE NOTICE '   - staff.01@qstream.vn, staff.02@qstream.vn, staff.03@qstream.vn, staff.04@qstream.vn (Staff)';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Sample Data Inserted:';
    RAISE NOTICE '   - 4 Government departments (each with 1 staff + 1 counter)';
    RAISE NOTICE '   - 16 Services (4 per department) with dynamic forms';
    RAISE NOTICE '   - 4 Service counters (1:1 mapping with departments)';
    RAISE NOTICE '   - 5 Queue tickets (3 completed with reviews)';
    RAISE NOTICE '   - 3 Customer feedback entries';
    RAISE NOTICE '   - Staff performance tracking data';
    RAISE NOTICE '   - QR codes for mobile access';
    RAISE NOTICE '   - System announcements';
    RAISE NOTICE '   - 3 Shift definitions (Morning, Afternoon, Night)';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Review System Data:';
    RAISE NOTICE '   - 3 Tickets with complete rating data';
    RAISE NOTICE '   - Service, staff, speed, and overall ratings';
    RAISE NOTICE '   - Detailed customer comments';
    RAISE NOTICE '   - Performance metrics integration';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Database ready for development and testing!';
    RAISE NOTICE '=====================================================';
END $$;