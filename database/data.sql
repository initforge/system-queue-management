-- =====================================================
-- QUEUE MANAGEMENT SYSTEM - SAMPLE DATA
-- =====================================================
-- Version: 5.0 (Minimal - matches schema.sql)

-- =====================================================
-- DEPARTMENTS
-- =====================================================

INSERT INTO departments (name, description, code) VALUES
('Phòng Kế hoạch Tổng hợp', 'Quản lý kế hoạch và tổng hợp các hoạt động', 'KHTH'),
('Phòng Tài chính Kế toán', 'Quản lý tài chính, ngân sách và kế toán', 'TCKT'),
('Phòng Hành chính Quản trị', 'Quản lý hành chính, nhân sự và văn thư', 'HCQT'),
('Phòng Công nghệ Thông tin', 'Quản lý hệ thống CNTT và dữ liệu điện tử', 'CNTT');

-- =====================================================
-- USERS (Password: Admin123!)
-- =====================================================

INSERT INTO users (username, password_hash, email, phone, full_name, role, department_id) VALUES
('admin', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'admin@qstream.vn', '0123456789', 'Quản trị viên Hệ thống', 'admin', 1),
('manager.01', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'manager.01@qstream.vn', '0123456790', 'Nguyễn Văn Quản lý', 'manager', 1),
('staff.01', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'staff.01@qstream.vn', '0123456791', 'Trần Thị Nhân viên', 'staff', 1),
('staff.02', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'staff.02@qstream.vn', '0123456792', 'Lê Văn Phục vụ', 'staff', 2),
('staff.03', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'staff.03@qstream.vn', '0123456793', 'Phạm Thị Hỗ trợ', 'staff', 3),
('staff.04', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 
 'staff.04@qstream.vn', '0123456794', 'Hoàng Văn Kỹ thuật', 'staff', 4);

-- =====================================================
-- SERVICES (16 total - 4 per department)
-- =====================================================

INSERT INTO services (name, description, department_id, service_code, estimated_duration) VALUES
-- Phòng Kế hoạch Tổng hợp
('Đăng ký kinh doanh', 'Dịch vụ đăng ký giấy phép kinh doanh', 1, 'DKKD', 30),
('Lập kế hoạch dự án', 'Hỗ trợ lập kế hoạch và quản lý dự án', 1, 'KHDA', 45),
('Báo cáo thống kê', 'Lập báo cáo và thống kê hoạt động', 1, 'BCTK', 30),
('Tư vấn quy trình', 'Tư vấn về quy trình và thủ tục hành chính', 1, 'TVQT', 25),
-- Phòng Tài chính Kế toán
('Nộp thuế', 'Dịch vụ nộp thuế và kê khai thuế', 2, 'NTHUE', 15),
('Thanh toán hóa đơn', 'Xử lý thanh toán các loại hóa đơn', 2, 'TTHD', 20),
('Kế toán doanh thu', 'Quản lý và kế toán doanh thu', 2, 'KTDT', 35),
('Kiểm tra tài chính', 'Kiểm tra và đối soát tài chính', 2, 'KTTC', 40),
-- Phòng Hành chính Quản trị
('Cấp giấy tờ', 'Dịch vụ cấp các loại giấy tờ, chứng nhận', 3, 'CGTO', 20),
('Cấp phép hoạt động', 'Cấp các loại giấy phép hoạt động', 3, 'CPHD', 50),
('Quản lý nhân sự', 'Xử lý hồ sơ và quản lý nhân sự', 3, 'QLNS', 30),
('Văn thư lưu trữ', 'Quản lý văn bản và lưu trữ hồ sơ', 3, 'VTLT', 15),
-- Phòng Công nghệ Thông tin
('Hỗ trợ kỹ thuật', 'Dịch vụ hỗ trợ kỹ thuật CNTT', 4, 'HTKT', 25),
('Cài đặt phần mềm', 'Hỗ trợ cài đặt và cấu hình phần mềm', 4, 'CDPM', 60),
('Bảo trì hệ thống', 'Bảo trì và nâng cấp hệ thống IT', 4, 'BTHT', 90),
('Đào tạo CNTT', 'Đào tạo sử dụng công nghệ thông tin', 4, 'DTCN', 120);

-- =====================================================
-- COUNTERS
-- =====================================================

INSERT INTO counters (name, number, department_id, assigned_staff_id) VALUES
('Quầy số 1', 1, 1, 3),
('Quầy số 2', 2, 2, 4),
('Quầy số 3', 3, 3, 5),
('Quầy số 4', 4, 4, 6);

-- =====================================================
-- SHIFTS
-- =====================================================

INSERT INTO shifts (id, name, shift_type, start_time, end_time, description) VALUES
('550e8400-e29b-41d4-a716-446655440001'::uuid, 'Ca Sáng', 'morning', '07:00:00', '15:00:00', 'Ca làm việc buổi sáng'),
('550e8400-e29b-41d4-a716-446655440002'::uuid, 'Ca Chiều', 'afternoon', '15:00:00', '23:00:00', 'Ca làm việc buổi chiều'),
('550e8400-e29b-41d4-a716-446655440003'::uuid, 'Ca Tối', 'night', '23:00:00', '07:00:00', 'Ca làm việc buổi tối');

-- =====================================================
-- SAMPLE QUEUE TICKETS
-- =====================================================

INSERT INTO queue_tickets (
    ticket_number, customer_name, customer_phone, customer_email, 
    service_id, department_id, status, priority, notes, 
    created_at, completed_at, overall_rating, review_comments, reviewed_at
) VALUES
('A001', 'Nguyễn Văn A', '0987654321', 'nguyenvana@email.com', 1, 1, 'completed', 'normal',
 'Hoàn thành thủ tục', '2026-01-08 08:00:00', '2026-01-08 08:30:00',
 5, 'Dịch vụ rất tốt!', '2026-01-08 08:35:00'),
('B002', 'Trần Thị B', '0987654322', 'tranthib@email.com', 5, 2, 'completed', 'normal',
 'Nộp thuế thành công', '2026-01-08 08:15:00', '2026-01-08 08:30:00',
 4, 'Xử lý nhanh chóng.', '2026-01-08 08:32:00'),
('C003', 'Lê Văn C', '0987654323', 'levanc@email.com', 9, 3, 'waiting', 'high',
 'Ưu tiên xử lý', '2026-01-08 09:00:00', NULL, NULL, NULL, NULL);

-- =====================================================
-- STAFF PERFORMANCE
-- =====================================================

INSERT INTO staff_performance (user_id, department_id, date, tickets_served, avg_service_time, total_rating_score, rating_count, avg_rating) VALUES
(3, 1, '2026-01-08', 2, 25.5, 10, 2, 5.0),
(4, 2, '2026-01-08', 1, 15.0, 4, 1, 4.0),
(5, 3, '2026-01-08', 0, 0, 0, 0, 0);

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'SAMPLE DATA INSERTED!';
    RAISE NOTICE '=====================================================';
    RAISE NOTICE 'Accounts (Password: Admin123!):';
    RAISE NOTICE '  admin@qstream.vn | manager.01@qstream.vn';
    RAISE NOTICE '  staff.01-04@qstream.vn';
    RAISE NOTICE '';
    RAISE NOTICE 'Data: 4 depts, 6 users, 16 services, 4 counters, 3 shifts';
    RAISE NOTICE '=====================================================';
END $$;