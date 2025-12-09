-- Knowledge Base Sample Data
-- This file contains initial categories and sample articles for the Knowledge Base

-- Insert Categories
INSERT INTO knowledge_base_categories (name, slug, description, icon, display_order, is_active) VALUES
('Quy trình nghiệp vụ', 'quy-trinh-nghiep-vu', 'Các quy trình và thủ tục nghiệp vụ trong hệ thống', '📖', 1, TRUE),
('Hướng dẫn dịch vụ', 'huong-dan-dich-vu', 'Hướng dẫn chi tiết về các dịch vụ', '🎓', 2, TRUE),
('Chính sách & Quy định', 'chinh-sach-quy-dinh', 'Các chính sách và quy định của công ty', '💼', 3, TRUE),
('Hướng dẫn sử dụng hệ thống', 'huong-dan-su-dung-he-thong', 'Hướng dẫn sử dụng các tính năng trong hệ thống', '🛠️', 4, TRUE),
('Tài liệu đào tạo', 'tai-lieu-dao-tao', 'Tài liệu và video hướng dẫn đào tạo', '📊', 5, TRUE),
('Team Resources', 'team-resources', 'Tài nguyên và thông tin nội bộ', '👥', 6, TRUE);

-- Insert Sample Articles
-- Note: author_id references users.id - assuming admin (id=1) or manager (id=2) exists

-- Article 1: Quy trình xử lý ticket
INSERT INTO knowledge_base_articles (title, slug, content, category_id, author_id, department_id, tags, is_published, is_featured, published_at) VALUES
(
  'Quy trình xử lý ticket chi tiết',
  'quy-trinh-xu-ly-ticket-chi-tiet',
  '## Quy trình xử lý ticket

### Bước 1: Tiếp nhận ticket
- Nhận ticket từ hệ thống hàng đợi
- Kiểm tra thông tin khách hàng và dịch vụ yêu cầu
- Xác nhận ticket trong hệ thống

### Bước 2: Xử lý yêu cầu
- Thực hiện dịch vụ theo quy trình
- Ghi chú các thông tin quan trọng
- Cập nhật tiến độ xử lý

### Bước 3: Hoàn thành
- Xác nhận dịch vụ đã hoàn thành
- Nhận đánh giá từ khách hàng
- Lưu lại thông tin vào hệ thống

**Lưu ý:** Luôn đảm bảo chất lượng dịch vụ và thái độ chuyên nghiệp.',
  1,
  (SELECT id FROM users WHERE role IN ('admin', 'manager') LIMIT 1), -- Use first admin/manager
  NULL, -- Global article
  ARRAY['ticket', 'quy trình', 'xử lý']::jsonb,
  TRUE,
  TRUE,
  NOW()
);

-- Article 2: Hướng dẫn tạo schedule
INSERT INTO knowledge_base_articles (title, slug, content, category_id, author_id, department_id, tags, is_published, is_featured, published_at) VALUES
(
  'Hướng dẫn tạo lịch làm việc tuần',
  'huong-dan-tao-lich-lam-viec-tuan',
  '## Hướng dẫn tạo lịch làm việc cho nhân viên

### Các bước thực hiện:

1. **Vào tab "Quản lý lịch làm việc"**
   - Chọn tuần cần tạo lịch
   - Xem tổng quan các ca làm việc

2. **Kéo thả nhân viên vào ca**
   - Chọn nhân viên từ danh sách
   - Kéo vào ca làm việc tương ứng
   - Hệ thống sẽ tự động kiểm tra xung đột

3. **Xác nhận và lưu**
   - Kiểm tra lại lịch làm việc
   - Nhấn "Lưu lịch làm việc"
   - Nhân viên sẽ nhận thông báo

**Tips:**
- Sử dụng tính năng "Copy tuần trước" để tiết kiệm thời gian
- Kiểm tra kỹ xung đột trước khi lưu
- Ưu tiên phân bổ nhân viên có kinh nghiệm cho ca quan trọng',
  4,
  (SELECT id FROM users WHERE role IN ('admin', 'manager') LIMIT 1),
  NULL,
  ARRAY['schedule', 'lịch làm việc', 'quản lý']::jsonb,
  TRUE,
  TRUE,
  NOW()
);

-- Article 3: Chính sách nghỉ phép
INSERT INTO knowledge_base_articles (title, slug, content, category_id, author_id, department_id, tags, is_published, is_featured, published_at) VALUES
(
  'Chính sách nghỉ phép và xin nghỉ',
  'chinh-sach-nghi-phep-va-xin-nghi',
  '## Chính sách nghỉ phép

### Các loại nghỉ phép:
1. **Nghỉ ốm** - Có giấy tờ y tế
2. **Nghỉ phép** - Nghỉ phép có lương
3. **Việc cá nhân** - Việc riêng không lương
4. **Khẩn cấp** - Trường hợp đột xuất

### Quy trình xin nghỉ:
1. Gửi đơn xin nghỉ ít nhất 2 ngày trước
2. Đợi quản lý duyệt
3. Nhận thông báo kết quả

### Quy định:
- Nghỉ phép: Tối đa 12 ngày/năm
- Nghỉ ốm: Cần giấy tờ y tế
- Nghỉ quá 3 ngày cần báo trước 1 tuần',
  3,
  (SELECT id FROM users WHERE role IN ('admin', 'manager') LIMIT 1),
  NULL,
  ARRAY['nghỉ phép', 'chính sách', 'quy định']::jsonb,
  TRUE,
  FALSE,
  NOW()
);

-- Article 4: FAQ
INSERT INTO knowledge_base_articles (title, slug, content, category_id, author_id, department_id, tags, is_published, is_featured, published_at) VALUES
(
  'Câu hỏi thường gặp (FAQ)',
  'cau-hoi-thuong-gap-faq',
  '## Câu hỏi thường gặp

### Q: Làm sao để xem lịch làm việc của tôi?
A: Vào tab "Ca làm việc" trong dashboard của bạn, bạn sẽ thấy lịch làm việc tuần hiện tại.

### Q: Tôi quên check-in thì phải làm sao?
A: Liên hệ với quản lý để được hỗ trợ. Hệ thống sẽ tự động ghi nhận first login của bạn.

### Q: Làm sao để xin nghỉ phép?
A: Vào tab "Ca làm việc" > "Xin nghỉ phép", điền form và gửi đơn. Quản lý sẽ duyệt trong vòng 24h.

### Q: Tôi có thể đổi ca với đồng nghiệp không?
A: Có, bạn có thể gửi yêu cầu đổi ca trong tab "Đổi ca làm việc". Cần có sự đồng ý của cả hai bên và quản lý.

### Q: Làm sao để xem thống kê hiệu suất?
A: Vào tab "Hiệu suất" để xem các thống kê về công việc của bạn.',
  4,
  (SELECT id FROM users WHERE role IN ('admin', 'manager') LIMIT 1),
  NULL,
  ARRAY['FAQ', 'câu hỏi', 'hướng dẫn']::jsonb,
  TRUE,
  TRUE,
  NOW()
);

-- Article 5: Dashboard Guide
INSERT INTO knowledge_base_articles (title, slug, content, category_id, author_id, department_id, tags, is_published, is_featured, published_at) VALUES
(
  'Hướng dẫn sử dụng Dashboard',
  'huong-dan-su-dung-dashboard',
  '## Hướng dẫn sử dụng Dashboard

### Các tab chính:

#### 1. Quản lý hàng đợi (Staff)
- Xem danh sách ticket đang chờ
- Nhận và xử lý ticket
- Hoàn thành ticket

#### 2. Ca làm việc
- Xem lịch làm việc cá nhân
- Xin nghỉ phép
- Đổi ca làm việc
- Xem thống kê cá nhân

#### 3. AI Helper
- Đặt câu hỏi về hệ thống
- Xem thống kê nhanh
- Nhận hướng dẫn sử dụng

#### 4. Hiệu suất
- Xem thống kê hiệu suất
- Theo dõi tiến độ công việc

#### 5. Kiến thức
- Tìm kiếm tài liệu
- Đọc hướng dẫn
- Xem tài nguyên nội bộ',
  4,
  (SELECT id FROM users WHERE role IN ('admin', 'manager') LIMIT 1),
  NULL,
  ARRAY['dashboard', 'hướng dẫn', 'sử dụng']::jsonb,
  TRUE,
  FALSE,
  NOW()
);

