--
-- PostgreSQL database dump
--

\restrict Y8CSghmeo8CWcN45shvkC6on7PASl3ntkMxBcXG2TZFG9aZmpiZoMhwYvVE5oSN

-- Dumped from database version 15.14
-- Dumped by pg_dump version 15.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.departments VALUES (1, 'Phòng Kế hoạch Tổng hợp', 'Quản lý kế hoạch và tổng hợp các hoạt động', 'KHTH', '54ac7a34-71c2-4199-8513-58caee49ac46', 30, '{"open": "08:00", "close": "17:00", "lunch_break": {"end": "13:00", "start": "12:00"}}', true, '2025-10-22 16:55:42.115556', '2025-10-22 16:55:42.115556');
INSERT INTO public.departments VALUES (2, 'Phòng Tài chính Kế toán', 'Quản lý tài chính, ngân sách và kế toán', 'TCKT', '249e47f6-13fa-4129-ad8e-0b1712ebbb95', 25, '{"open": "08:00", "close": "17:00", "lunch_break": {"end": "13:00", "start": "12:00"}}', true, '2025-10-22 16:55:42.115556', '2025-10-22 16:55:42.115556');
INSERT INTO public.departments VALUES (3, 'Phòng Hành chính Quản trị', 'Quản lý hành chính, nhân sự và văn thư', 'HCQT', 'f7fa6058-2e2b-457d-9ba1-13c3518dbf07', 20, '{"open": "08:00", "close": "17:00", "lunch_break": {"end": "13:00", "start": "12:00"}}', true, '2025-10-22 16:55:42.115556', '2025-10-22 16:55:42.115556');
INSERT INTO public.departments VALUES (4, 'Phòng Công nghệ Thông tin', 'Quản lý hệ thống CNTT và dữ liệu điện tử', 'CNTT', '860bb828-2054-4697-a528-d926663cf17e', 15, '{"open": "08:00", "close": "17:00", "lunch_break": {"end": "13:00", "start": "12:00"}}', true, '2025-10-22 16:55:42.115556', '2025-10-22 16:55:42.115556');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.users VALUES (1, 'admin', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 'admin@qstream.vn', '0123456789', 'Quản trị viên Hệ thống', 'admin', 1, true, NULL, NULL, '2025-10-22 16:55:42.118506', '2025-10-22 16:55:42.118506');
INSERT INTO public.users VALUES (4, 'staff.02', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 'staff.02@qstream.vn', '0123456792', 'Lê Văn Phục vụ', 'staff', 2, true, NULL, '2025-12-15 08:47:24.811151', '2025-10-22 16:55:42.118506', '2025-10-22 16:55:42.118506');
INSERT INTO public.users VALUES (5, 'staff.03', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 'staff.03@qstream.vn', '0123456793', 'Phạm Thị Hỗ trợ', 'staff', 3, true, NULL, NULL, '2025-10-22 16:55:42.118506', '2025-10-22 16:55:42.118506');
INSERT INTO public.users VALUES (6, 'staff.04', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 'staff.04@qstream.vn', '0123456794', 'Hoàng Văn Kỹ thuật', 'staff', 4, true, NULL, NULL, '2025-10-22 17:18:54.427726', '2025-10-22 17:18:54.427726');
INSERT INTO public.users VALUES (2, 'manager.01', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 'manager.01@qstream.vn', '0123456790', 'Nguyễn Văn Quản lý', 'manager', 1, true, NULL, '2026-01-07 21:11:15.328792', '2025-10-22 16:55:42.118506', '2025-10-22 16:55:42.118506');
INSERT INTO public.users VALUES (3, 'staff.01', '$2b$12$evfrHfCVUoh/H4mQfP4QReVR1U8hFqRTMNVumFCf6/tHjR/RpRhZK', 'staff.01@qstream.vn', '0123456791', 'Trần Thị Nhân viên', 'staff', 1, true, NULL, '2026-01-07 21:11:20.457234', '2025-10-22 16:55:42.118506', '2025-10-22 16:55:42.118506');


--
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: ai_conversations; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.ai_conversations VALUES (1, 3, '91f5b015-0c47-4821-8bf5-a8f6db339f0d', 'user', 'Hiệu suất của t như thế nào', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 06:32:12.95964+00');
INSERT INTO public.ai_conversations VALUES (2, 3, '91f5b015-0c47-4821-8bf5-a8f6db339f0d', 'assistant', 'Xin lỗi, dịch vụ AI hiện không khả dụng. Vui lòng liên hệ quản trị viên.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 06:32:12.95964+00');
INSERT INTO public.ai_conversations VALUES (3, 3, '6af7d0b4-9e76-4960-a869-563b6c88361f', 'user', 'Thống kê hiệu suất của tôi thế nào?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 09:24:34.720695+00');
INSERT INTO public.ai_conversations VALUES (4, 3, '6af7d0b4-9e76-4960-a869-563b6c88361f', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 400 API key not valid. Please pass a valid API key. [reason: "API_KEY_INVALID"
domain: "googleapis.com"
metadata {
  key: "service"
  value: "generativelanguage.googleapis.com"
}
, locale: "en-US"
message: "API key not valid. Please pass a valid API key."
]', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 09:24:34.720695+00');
INSERT INTO public.ai_conversations VALUES (5, 3, '6af7d0b4-9e76-4960-a869-563b6c88361f', 'user', 'Lịch làm việc t có chưa', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 09:24:53.85099+00');
INSERT INTO public.ai_conversations VALUES (6, 3, '6af7d0b4-9e76-4960-a869-563b6c88361f', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 400 API key not valid. Please pass a valid API key. [reason: "API_KEY_INVALID"
domain: "googleapis.com"
metadata {
  key: "service"
  value: "generativelanguage.googleapis.com"
}
, locale: "en-US"
message: "API key not valid. Please pass a valid API key."
]', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 09:24:53.85099+00');
INSERT INTO public.ai_conversations VALUES (7, 3, 'd63363b2-047b-443b-873c-0f1cdaa42624', 'user', 'Hello', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 11:43:23.907384+00');
INSERT INTO public.ai_conversations VALUES (8, 3, 'd63363b2-047b-443b-873c-0f1cdaa42624', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 400 API key not valid. Please pass a valid API key. [reason: "API_KEY_INVALID"
domain: "googleapis.com"
metadata {
  key: "service"
  value: "generativelanguage.googleapis.com"
}
, locale: "en-US"
message: "API key not valid. Please pass a valid API key."
]', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 11:43:23.907384+00');
INSERT INTO public.ai_conversations VALUES (9, 3, 'dbfc04ca-6bce-4ddf-a9ec-511cdfcbeb04', 'user', 'Lịch làm việc tuần này của tôi?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 12:02:52.117017+00');
INSERT INTO public.ai_conversations VALUES (10, 3, 'dbfc04ca-6bce-4ddf-a9ec-511cdfcbeb04', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 400 API key not valid. Please pass a valid API key. [reason: "API_KEY_INVALID"
domain: "googleapis.com"
metadata {
  key: "service"
  value: "generativelanguage.googleapis.com"
}
, locale: "en-US"
message: "API key not valid. Please pass a valid API key."
]', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 12:02:52.117017+00');
INSERT INTO public.ai_conversations VALUES (11, 3, '9b1423bf-6633-4da3-8c84-fc1f658999dc', 'user', 'Thống kê hiệu suất của tôi thế nào?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 12:26:55.957943+00');
INSERT INTO public.ai_conversations VALUES (12, 3, '9b1423bf-6633-4da3-8c84-fc1f658999dc', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 400 API key not valid. Please pass a valid API key. [reason: "API_KEY_INVALID"
domain: "googleapis.com"
metadata {
  key: "service"
  value: "generativelanguage.googleapis.com"
}
, locale: "en-US"
message: "API key not valid. Please pass a valid API key."
]', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 12:26:55.957943+00');
INSERT INTO public.ai_conversations VALUES (13, 3, '9b1423bf-6633-4da3-8c84-fc1f658999dc', 'user', 'Trả lời random', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 12:27:05.664362+00');
INSERT INTO public.ai_conversations VALUES (14, 3, '9b1423bf-6633-4da3-8c84-fc1f658999dc', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 400 API key not valid. Please pass a valid API key. [reason: "API_KEY_INVALID"
domain: "googleapis.com"
metadata {
  key: "service"
  value: "generativelanguage.googleapis.com"
}
, locale: "en-US"
message: "API key not valid. Please pass a valid API key."
]', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 12:27:05.664362+00');
INSERT INTO public.ai_conversations VALUES (15, 3, 'eaa7619f-fc4a-4622-a44d-bfb1b8dc64aa', 'user', 'Trả lời t 1 tiếng', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 12:28:06.583203+00');
INSERT INTO public.ai_conversations VALUES (16, 3, 'eaa7619f-fc4a-4622-a44d-bfb1b8dc64aa', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 400 API key not valid. Please pass a valid API key. [reason: "API_KEY_INVALID"
domain: "googleapis.com"
metadata {
  key: "service"
  value: "generativelanguage.googleapis.com"
}
, locale: "en-US"
message: "API key not valid. Please pass a valid API key."
]', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 12:28:06.583203+00');
INSERT INTO public.ai_conversations VALUES (17, 3, '7b7b9bc2-980d-417b-96b7-8291fd769807', 'user', 'Lịch làm việc tuần này của tôi?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 13:10:11.233163+00');
INSERT INTO public.ai_conversations VALUES (18, 3, '7b7b9bc2-980d-417b-96b7-8291fd769807', 'assistant', 'Xin lỗi, dịch vụ AI hiện không khả dụng. Vui lòng liên hệ quản trị viên.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 13:10:11.233163+00');
INSERT INTO public.ai_conversations VALUES (19, 3, '7b7b9bc2-980d-417b-96b7-8291fd769807', 'user', 'Trời ơi', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 13:10:17.768418+00');
INSERT INTO public.ai_conversations VALUES (20, 3, '7b7b9bc2-980d-417b-96b7-8291fd769807', 'assistant', 'Xin lỗi, dịch vụ AI hiện không khả dụng. Vui lòng liên hệ quản trị viên.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-01 13:10:17.768418+00');
INSERT INTO public.ai_conversations VALUES (21, 3, '1aaa6811-41ec-4eb6-80b2-ae9e6c6c14fc', 'user', 'Cách sử dụng hệ thống?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-02 02:28:08.485582+00');
INSERT INTO public.ai_conversations VALUES (22, 3, '1aaa6811-41ec-4eb6-80b2-ae9e6c6c14fc', 'assistant', 'Chào bạn Trần Thị Nhân viên! Với vai trò là nhân viên (staff) trong hệ thống Quản lý hàng đợi, bạn có thể sử dụng hệ thống để:

*   **Xem thông tin cá nhân:** Bạn có thể xem thông tin cá nhân của mình như tên, phòng ban, thông tin liên hệ, v.v.

*   **Xem lịch làm việc:** Bạn có thể xem lịch làm việc của mình để biết thời gian làm việc, ca trực và các nhiệm vụ được giao.

*   **Xem thống kê hiệu suất:** Bạn có thể xem thống kê về hiệu suất làm việc của mình, ví dụ như số lượng khách hàng đã phục vụ, thời gian phục vụ trung bình, v.v. Điều này giúp bạn theo dõi và cải thiện hiệu quả công việc.

Để thực hiện các thao tác trên, bạn có thể:

1.  **Sử dụng menu chính:** Menu chính thường hiển thị các mục như "Thông tin cá nhân", "Lịch làm việc", "Thống kê", v.v. Bạn có thể chọn mục tương ứng để xem thông tin.
2.  **Sử dụng thanh tìm kiếm:** Nếu bạn muốn tìm kiếm một chức năng cụ thể, bạn có thể sử dụng thanh tìm kiếm và nhập từ khóa liên quan.
3.  **Tham khảo hướng dẫn chi tiết:** Nếu bạn gặp khó khăn trong quá trình sử dụng, bạn có thể tìm kiếm tài liệu hướng dẫn chi tiết trong hệ thống hoặc liên hệ với bộ phận hỗ trợ kỹ thuật.

Bạn có muốn tôi hướng dẫn cụ thể về một chức năng nào không? Ví dụ, bạn có muốn tôi hướng dẫn cách xem lịch làm việc của mình không?
', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-02 02:28:08.485582+00');
INSERT INTO public.ai_conversations VALUES (23, 3, '1aaa6811-41ec-4eb6-80b2-ae9e6c6c14fc', 'user', 'hàng đợi đang có ai đó', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-02 02:34:41.008004+00');
INSERT INTO public.ai_conversations VALUES (24, 3, '1aaa6811-41ec-4eb6-80b2-ae9e6c6c14fc', 'assistant', 'Chào bạn Trần Thị Nhân viên! Để xem thông tin về hàng đợi hiện tại, bạn vui lòng cho biết bạn muốn xem thông tin cụ thể nào? Ví dụ:

*   **Số lượng người đang chờ:** Tổng số người đang chờ trong hàng đợi.
*   **Danh sách những người đang chờ:** Thông tin chi tiết về từng người đang chờ (nếu được phép truy cập).
*   **Thời gian chờ trung bình:** Ước tính thời gian chờ trung bình của khách hàng trong hàng đợi.
*   **Hàng đợi ưu tiên:** Có những ai đang chờ thuộc diện ưu tiên (nếu có).

Để cung cấp thông tin chính xác và đầy đủ, tôi cần biết bạn muốn xem thông tin gì. Sau đó, tôi có thể sử dụng một function call (nếu cần thiết) để truy xuất dữ liệu từ hệ thống và hiển thị cho bạn. Ví dụ, nếu bạn muốn biết số lượng người đang chờ, tôi có thể sử dụng function call `get_queue_length()`.
', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-02 02:34:41.008004+00');
INSERT INTO public.ai_conversations VALUES (25, 3, 'bdae6d59-887a-4c9a-ad67-06d4c45b43ce', 'user', 'Thống kê hiệu suất của tôi thế nào?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-14 23:49:24.2638+00');
INSERT INTO public.ai_conversations VALUES (26, 3, 'bdae6d59-887a-4c9a-ad67-06d4c45b43ce', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 403 Your API key was reported as leaked. Please use another API key.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-14 23:49:24.2638+00');
INSERT INTO public.ai_conversations VALUES (27, 3, 'e958dd51-66e2-4856-b5d8-c39bf604e2c2', 'user', 'Thống kê hiệu suất của tôi thế nào?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-14 23:57:18.487963+00');
INSERT INTO public.ai_conversations VALUES (28, 3, 'e958dd51-66e2-4856-b5d8-c39bf604e2c2', 'user', 'Queue', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2025-12-14 23:57:28.675622+00');
INSERT INTO public.ai_conversations VALUES (29, 2, 'cbfcf2c3-d0d5-4e29-8b6f-e2afec15e8ae', 'user', 'Hàng đợi đang có ai chờ không', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2025-12-15 05:42:23.877136+00');
INSERT INTO public.ai_conversations VALUES (30, 2, 'cbfcf2c3-d0d5-4e29-8b6f-e2afec15e8ae', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/usage?tab=rate-limit. 
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count, limit: 0, model: gemini-2.0-flash
Please retry in 36.008944567s. [links {
  description: "Learn more about Gemini API quotas"
  url: "https://ai.google.dev/gemini-api/docs/rate-limits"
}
, violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "location"
    value: "global"
  }
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "location"
    value: "global"
  }
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count"
  quota_id: "GenerateContentInputTokensPerModelPerMinute-FreeTier"
  quota_dimensions {
    key: "location"
    value: "global"
  }
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash"
  }
}
, retry_delay {
  seconds: 36
}
]', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2025-12-15 05:42:23.877136+00');
INSERT INTO public.ai_conversations VALUES (31, 2, 'cbfcf2c3-d0d5-4e29-8b6f-e2afec15e8ae', 'user', 'Hàng đợi đang có ai chờ không', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2025-12-15 05:44:29.890578+00');
INSERT INTO public.ai_conversations VALUES (32, 2, 'cbfcf2c3-d0d5-4e29-8b6f-e2afec15e8ae', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/usage?tab=rate-limit. 
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count, limit: 0, model: gemini-2.0-flash
Please retry in 29.848681657s. [links {
  description: "Learn more about Gemini API quotas"
  url: "https://ai.google.dev/gemini-api/docs/rate-limits"
}
, violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "location"
    value: "global"
  }
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_requests"
  quota_id: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"
  quota_dimensions {
    key: "location"
    value: "global"
  }
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash"
  }
}
violations {
  quota_metric: "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count"
  quota_id: "GenerateContentInputTokensPerModelPerMinute-FreeTier"
  quota_dimensions {
    key: "location"
    value: "global"
  }
  quota_dimensions {
    key: "model"
    value: "gemini-2.0-flash"
  }
}
, retry_delay {
  seconds: 29
}
]', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2025-12-15 05:44:29.890578+00');
INSERT INTO public.ai_conversations VALUES (33, 2, 'cbfcf2c3-d0d5-4e29-8b6f-e2afec15e8ae', 'user', 'Hàng đợi đang có ai chờ không', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2025-12-15 05:46:36.093005+00');
INSERT INTO public.ai_conversations VALUES (34, 2, 'cbfcf2c3-d0d5-4e29-8b6f-e2afec15e8ae', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 429 You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/usage?tab=rate-limit. ', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2025-12-15 05:46:36.093005+00');
INSERT INTO public.ai_conversations VALUES (35, 2, '6bdf58c6-bbbf-42c3-ae69-f56dabd2f667', 'user', 'Hỏi m gì đây ta', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2025-12-15 06:31:36.275859+00');
INSERT INTO public.ai_conversations VALUES (36, 2, '6bdf58c6-bbbf-42c3-ae69-f56dabd2f667', 'assistant', '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).

Vui lòng:
1. Đợi vài phút rồi thử lại
2. Kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit
3. Nâng cấp gói API nếu cần thiết', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2025-12-15 06:31:36.275859+00');
INSERT INTO public.ai_conversations VALUES (37, 3, '9833afe5-a873-451f-a695-c47797fc29a8', 'user', 'Hiệu suất của t tháng nay ntn', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 12:55:08.490288+00');
INSERT INTO public.ai_conversations VALUES (38, 3, '9833afe5-a873-451f-a695-c47797fc29a8', 'assistant', '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).

Vui lòng:
1. Đợi vài phút rồi thử lại
2. Kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit
3. Nâng cấp gói API nếu cần thiết', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 12:55:08.490288+00');
INSERT INTO public.ai_conversations VALUES (39, 3, '9833afe5-a873-451f-a695-c47797fc29a8', 'user', 'Lịch làm việc ngày mai có không', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 12:55:19.033702+00');
INSERT INTO public.ai_conversations VALUES (40, 3, '9833afe5-a873-451f-a695-c47797fc29a8', 'assistant', '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).

Vui lòng:
1. Đợi vài phút rồi thử lại
2. Kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit
3. Nâng cấp gói API nếu cần thiết', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 12:55:19.033702+00');
INSERT INTO public.ai_conversations VALUES (41, 2, '802fdb2f-dd81-45f9-b692-2d34d05bde90', 'user', 'Thống kê hiệu suất của tôi thế nào?', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2026-01-07 12:58:01.081796+00');
INSERT INTO public.ai_conversations VALUES (42, 2, '802fdb2f-dd81-45f9-b692-2d34d05bde90', 'assistant', '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).

Vui lòng:
1. Đợi vài phút rồi thử lại
2. Kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit
3. Nâng cấp gói API nếu cần thiết', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2026-01-07 12:58:01.081796+00');
INSERT INTO public.ai_conversations VALUES (43, 2, '802fdb2f-dd81-45f9-b692-2d34d05bde90', 'user', 'THống kê', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2026-01-07 12:58:05.921005+00');
INSERT INTO public.ai_conversations VALUES (44, 2, '802fdb2f-dd81-45f9-b692-2d34d05bde90', 'assistant', '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).

Vui lòng:
1. Đợi vài phút rồi thử lại
2. Kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit
3. Nâng cấp gói API nếu cần thiết', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": null}}', NULL, '2026-01-07 12:58:05.921005+00');
INSERT INTO public.ai_conversations VALUES (45, 2, '5e34eecc-e0c6-45f6-a08d-638cbcb284a1', 'user', 'Lịch làm việc hôm nay như thế nào', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 14:27:30.123204+00');
INSERT INTO public.ai_conversations VALUES (46, 2, '5e34eecc-e0c6-45f6-a08d-638cbcb284a1', 'assistant', '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).

Vui lòng:
1. Đợi vài phút rồi thử lại
2. Kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit
3. Nâng cấp gói API nếu cần thiết', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 14:27:30.123204+00');
INSERT INTO public.ai_conversations VALUES (47, 2, 'b32ea43f-eb48-49d4-a0bb-1c8aaa6f9ad0', 'user', 'alo', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:46:14.062772+00');
INSERT INTO public.ai_conversations VALUES (48, 2, 'b32ea43f-eb48-49d4-a0bb-1c8aaa6f9ad0', 'assistant', '⚠️ Bạn đã vượt quá giới hạn sử dụng API (Rate Limit).

Vui lòng:
1. Đợi vài phút rồi thử lại
2. Kiểm tra quota tại: https://ai.dev/usage?tab=rate-limit
3. Nâng cấp gói API nếu cần thiết', '{"user": {"id": 2, "full_name": "Nguy\u1ec5n V\u0103n Qu\u1ea3n l\u00fd", "role": "manager", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:46:14.062772+00');
INSERT INTO public.ai_conversations VALUES (49, 3, 'e407cb9d-510b-49d4-850e-3fd8b629736d', 'user', 'hello bạn', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:49:30.210209+00');
INSERT INTO public.ai_conversations VALUES (63, 3, 'd15e58e1-12b6-448a-927c-4ab6b6d78e35', 'user', 'Hàng đợi của t đang có ai', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:12:18.288262+00');
INSERT INTO public.ai_conversations VALUES (50, 3, 'e407cb9d-510b-49d4-850e-3fd8b629736d', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 404 models/gemini-1.5-pro is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:49:30.210209+00');
INSERT INTO public.ai_conversations VALUES (51, 3, 'e407cb9d-510b-49d4-850e-3fd8b629736d', 'user', 'lại nào', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:49:44.646466+00');
INSERT INTO public.ai_conversations VALUES (52, 3, 'e407cb9d-510b-49d4-850e-3fd8b629736d', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 404 models/gemini-1.5-pro is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:49:44.646466+00');
INSERT INTO public.ai_conversations VALUES (53, 3, 'f8f433ef-de22-47e8-97b1-32040063b033', 'user', 'Hi', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:51:38.424088+00');
INSERT INTO public.ai_conversations VALUES (54, 3, 'f8f433ef-de22-47e8-97b1-32040063b033', 'assistant', 'Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu: 404 models/gemini-pro is not found for API version v1beta, or is not supported for generateContent. Call ListModels to see the list of available models and their supported methods.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:51:38.424088+00');
INSERT INTO public.ai_conversations VALUES (55, 3, 'f8f433ef-de22-47e8-97b1-32040063b033', 'user', 'hellu', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:53:47.330487+00');
INSERT INTO public.ai_conversations VALUES (56, 3, 'f8f433ef-de22-47e8-97b1-32040063b033', 'assistant', 'Chào bạn Trần Thị Nhân viên, rất vui được hỗ trợ bạn!

Với vai trò là Staff, bạn có thể thực hiện các tác vụ sau đây trên hệ thống Quản lý hàng đợi:

*   **Xem thông tin cá nhân:** Bạn có thể xem lại các thông tin cá nhân đã đăng ký trên hệ thống.
*   **Xem lịch làm việc:** Nắm bắt lịch trình làm việc của bản thân để sắp xếp công việc hiệu quả.
*   **Xem thống kê hiệu suất:** Theo dõi và đánh giá hiệu suất làm việc của mình.
*   **Được hướng dẫn sử dụng hệ thống:** Nếu có bất kỳ câu hỏi nào về cách sử dụng hệ thống, đừng ngần ngại hỏi nhé.

Bạn cần tôi hỗ trợ gì ạ? Ví dụ, bạn muốn xem lịch làm việc của mình hay có câu hỏi về một chức năng nào đó của hệ thống không?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:53:47.330487+00');
INSERT INTO public.ai_conversations VALUES (57, 3, 'f8f433ef-de22-47e8-97b1-32040063b033', 'user', 'Có ai trong hàng đợi của t không', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:54:01.827792+00');
INSERT INTO public.ai_conversations VALUES (58, 3, 'f8f433ef-de22-47e8-97b1-32040063b033', 'assistant', 'Chào bạn Trần Thị Nhân viên,

Để xem ai đang trong hàng đợi của bạn, bạn có thể sử dụng chức năng xem thống kê hiệu suất. Chức năng này sẽ cung cấp cho bạn thông tin chi tiết về các lượt khách đã được phục vụ, đang chờ, cũng như hiệu suất làm việc của bạn.

Bạn có muốn tôi hỗ trợ bạn truy cập vào chức năng xem thống kê hiệu suất không? Hoặc bạn có câu hỏi cụ thể nào về thống kê hiệu suất không?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:54:01.827792+00');
INSERT INTO public.ai_conversations VALUES (59, 3, 'f8f433ef-de22-47e8-97b1-32040063b033', 'user', 'ok làm theo ý m đi', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:54:18.439396+00');
INSERT INTO public.ai_conversations VALUES (60, 3, 'f8f433ef-de22-47e8-97b1-32040063b033', 'assistant', 'Tuyệt vời! Để xem thống kê hiệu suất của bạn, vui lòng thực hiện các bước sau:

1.  Trên thanh điều hướng chính của hệ thống, bạn tìm đến mục "**Thống kê**".
2.  Trong mục "**Thống kê**", chọn "**Hiệu suất cá nhân**".
3.  Tại đây, bạn có thể xem được các thông tin như:
    *   Số lượng khách hàng đang chờ.
    *   Số lượng khách hàng đã được phục vụ trong khoảng thời gian bạn chọn (ví dụ: hôm nay, tuần này, tháng này).
    *   Thời gian trung bình xử lý một khách hàng.
    *   Và các chỉ số hiệu suất khác.

Bạn có muốn tôi thực hiện **function call** để hiển thị trực tiếp thống kê hiệu suất của bạn ngay bây giờ không? Hoặc bạn có cần hướng dẫn thêm về cách xem một loại dữ liệu cụ thể nào trong thống kê hiệu suất không ạ?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}}', NULL, '2026-01-07 17:54:18.439396+00');
INSERT INTO public.ai_conversations VALUES (61, 3, 'd1564f99-db1d-4cfa-9921-ef863a0090d0', 'user', 'có khách nào trong hàng đợi không', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}, "my_schedule": [{"date": "2026-01-07", "shift_id": "6906373c-f27d-435d-81a9-80a614aeabba", "status": "scheduled"}, {"date": "2026-01-06", "shift_id": "e2b4ea03-c2a5-4e6e-b0a3-cb567fdb9820", "status": "scheduled"}], "my_performance_today": {"tickets_served": 0, "avg_rating": 0}}', NULL, '2026-01-07 18:01:50.634962+00');
INSERT INTO public.ai_conversations VALUES (62, 3, 'd1564f99-db1d-4cfa-9921-ef863a0090d0', 'assistant', 'Tôi không có thông tin về số lượng khách trong hàng đợi. Tuy nhiên, bạn có thể sử dụng tính năng "Quản lý hàng đợi" để kiểm tra.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p", "code": "KHTH"}, "my_schedule": [{"date": "2026-01-07", "shift_id": "6906373c-f27d-435d-81a9-80a614aeabba", "status": "scheduled"}, {"date": "2026-01-06", "shift_id": "e2b4ea03-c2a5-4e6e-b0a3-cb567fdb9820", "status": "scheduled"}], "my_performance_today": {"tickets_served": 0, "avg_rating": 0}}', NULL, '2026-01-07 18:01:50.634962+00');
INSERT INTO public.ai_conversations VALUES (64, 3, 'd15e58e1-12b6-448a-927c-4ab6b6d78e35', 'assistant', 'Đã xảy ra lỗi: ''object''', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:12:18.288262+00');
INSERT INTO public.ai_conversations VALUES (65, 3, 'd52f377f-0972-4fd2-9914-b300f11b1e6c', 'user', 'T hỏi m được những gì', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:14:24.632026+00');
INSERT INTO public.ai_conversations VALUES (66, 3, 'd52f377f-0972-4fd2-9914-b300f11b1e6c', 'assistant', 'Đã xảy ra lỗi: ''object''', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:14:24.632026+00');
INSERT INTO public.ai_conversations VALUES (67, 3, 'd52f377f-0972-4fd2-9914-b300f11b1e6c', 'user', 'lỗi à', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:16:20.994677+00');
INSERT INTO public.ai_conversations VALUES (68, 3, 'd52f377f-0972-4fd2-9914-b300f11b1e6c', 'assistant', 'Đã xảy ra lỗi: ''object''', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:16:20.994677+00');
INSERT INTO public.ai_conversations VALUES (69, 3, 'd52f377f-0972-4fd2-9914-b300f11b1e6c', 'user', 'help help', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:16:42.81137+00');
INSERT INTO public.ai_conversations VALUES (70, 3, 'd52f377f-0972-4fd2-9914-b300f11b1e6c', 'assistant', 'Đã xảy ra lỗi: ''object''', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:16:42.81137+00');
INSERT INTO public.ai_conversations VALUES (71, 3, 'd52f377f-0972-4fd2-9914-b300f11b1e6c', 'user', 'ok v trả lời được chưa', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:18:30.608707+00');
INSERT INTO public.ai_conversations VALUES (72, 3, 'd52f377f-0972-4fd2-9914-b300f11b1e6c', 'assistant', 'Đã xảy ra lỗi: ''object''', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:18:30.608707+00');
INSERT INTO public.ai_conversations VALUES (73, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'user', 'Siuuuuuuuuu', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:20:58.670771+00');
INSERT INTO public.ai_conversations VALUES (74, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'assistant', 'Bạn có thể nói rõ hơn yêu cầu của mình được không?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:20:58.670771+00');
INSERT INTO public.ai_conversations VALUES (75, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'user', 'Hàng đợi của t đang có ai không', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:21:09.280682+00');
INSERT INTO public.ai_conversations VALUES (76, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'assistant', 'Đã xảy ra lỗi: Invalid operation: The `response.text` quick accessor requires the response to contain a valid `Part`, but none were returned. The candidate''s [finish_reason](https://ai.google.dev/api/generate-content#finishreason) is 1.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:21:09.280682+00');
INSERT INTO public.ai_conversations VALUES (77, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'user', 'melm mle', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:23:33.368626+00');
INSERT INTO public.ai_conversations VALUES (78, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'assistant', 'Bạn có thể nói rõ hơn yêu cầu của mình được không?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:23:33.368626+00');
INSERT INTO public.ai_conversations VALUES (79, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'user', 'hàng đợi của t đang có ai', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:23:45.394358+00');
INSERT INTO public.ai_conversations VALUES (80, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'assistant', 'Đã xảy ra lỗi: Invalid operation: The `response.text` quick accessor requires the response to contain a valid `Part`, but none were returned. The candidate''s [finish_reason](https://ai.google.dev/api/generate-content#finishreason) is 1.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:23:45.394358+00');
INSERT INTO public.ai_conversations VALUES (81, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'user', 'blah blah', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:26:14.210193+00');
INSERT INTO public.ai_conversations VALUES (82, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'assistant', 'Bạn có thể nói rõ hơn yêu cầu của mình được không?', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:26:14.210193+00');
INSERT INTO public.ai_conversations VALUES (83, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'user', 'Hàng đợi', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:26:22.540664+00');
INSERT INTO public.ai_conversations VALUES (84, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'assistant', 'Để xem thông tin về hàng đợi, bạn vui lòng truy cập vào mục **Quản lý hàng đợi** trên hệ thống QStream nhé. Tại đó, bạn có thể xem số lượng khách hàng đang chờ và gọi phiếu để phục vụ.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:26:22.540664+00');
INSERT INTO public.ai_conversations VALUES (85, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'user', 'Đang có ai trên hàng đợi', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:26:33.964399+00');
INSERT INTO public.ai_conversations VALUES (86, 3, 'f846afb9-1a72-4cd1-9304-90cf43a5da7d', 'assistant', 'Để xem ai đang có mặt trên hàng đợi, bạn vui lòng truy cập vào mục **Quản lý hàng đợi** trên hệ thống QStream nhé. Tại đó, bạn có thể xem danh sách khách hàng đang chờ.', '{"user": {"id": 3, "full_name": "Tr\u1ea7n Th\u1ecb Nh\u00e2n vi\u00ean", "username": "staff.01", "role": "staff", "department_id": 1}, "department": {"id": 1, "name": "Ph\u00f2ng K\u1ebf ho\u1ea1ch T\u1ed5ng h\u1ee3p"}}', NULL, '2026-01-07 18:26:33.964399+00');


--
-- Data for Name: announcements; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.announcements VALUES (1, 'Thông báo bảo trì hệ thống', 'Hệ thống sẽ được bảo trì từ 18:00-20:00 hôm nay để nâng cấp tính năng mới. Vui lòng hoàn tất các giao dịch trước thời gian này.', 'maintenance', 'all', NULL, 1, true, '2025-10-22 16:55:42.146151', '2025-10-22 20:00:00', '2025-10-22 16:55:42.146151');
INSERT INTO public.announcements VALUES (2, 'Cập nhật quy trình đăng ký kinh doanh', 'Từ ngày 25/10/2025, quy trình đăng ký kinh doanh sẽ có một số thay đổi để đơn giản hóa thủ tục. Vui lòng tham khảo hướng dẫn mới.', 'general', 'staff', 1, 2, true, '2025-10-22 16:55:42.146151', '2025-10-30 23:59:59', '2025-10-22 16:55:42.146151');


--
-- Data for Name: counters; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.counters VALUES (1, 'Quầy số 1', 1, 1, 3, true, '2025-10-22 16:55:42.124976', '2025-10-22 16:55:42.124976');
INSERT INTO public.counters VALUES (3, 'Quầy số 2', 2, 2, 4, true, '2025-10-22 16:55:42.124976', '2025-10-22 16:55:42.124976');
INSERT INTO public.counters VALUES (4, 'Quầy số 3', 3, 3, 5, true, '2025-10-22 16:55:42.124976', '2025-10-22 16:55:42.124976');
INSERT INTO public.counters VALUES (5, 'Quầy số 4', 4, 4, 6, true, '2025-10-22 16:55:42.124976', '2025-10-22 16:55:42.124976');


--
-- Data for Name: daily_login_logs; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.daily_login_logs VALUES (1, 2, '2025-12-01', '2025-12-01 06:29:48.098711+00', NULL, '2025-12-01 06:29:48.118433+00');
INSERT INTO public.daily_login_logs VALUES (2, 3, '2025-12-01', '2025-12-01 06:31:37.932488+00', NULL, '2025-12-01 06:31:37.945728+00');
INSERT INTO public.daily_login_logs VALUES (3, 3, '2025-12-02', '2025-12-02 02:26:55.237885+00', NULL, '2025-12-02 02:26:55.247705+00');
INSERT INTO public.daily_login_logs VALUES (4, 3, '2025-12-14', '2025-12-14 23:38:09.785461+00', NULL, '2025-12-14 23:38:09.794851+00');
INSERT INTO public.daily_login_logs VALUES (5, 2, '2025-12-14', '2025-12-14 23:41:19.722467+00', NULL, '2025-12-14 23:41:19.726248+00');
INSERT INTO public.daily_login_logs VALUES (6, 2, '2025-12-15', '2025-12-15 05:41:46.655215+00', NULL, '2025-12-15 05:41:46.66513+00');
INSERT INTO public.daily_login_logs VALUES (7, 3, '2025-12-15', '2025-12-15 08:44:17.567829+00', NULL, '2025-12-15 08:44:17.576717+00');
INSERT INTO public.daily_login_logs VALUES (8, 4, '2025-12-15', '2025-12-15 08:47:24.609033+00', NULL, '2025-12-15 08:47:24.614918+00');
INSERT INTO public.daily_login_logs VALUES (9, 3, '2026-01-07', '2026-01-07 12:51:47.425117+00', NULL, '2026-01-07 12:51:47.449492+00');
INSERT INTO public.daily_login_logs VALUES (10, 2, '2026-01-07', '2026-01-07 12:56:47.632166+00', NULL, '2026-01-07 12:56:47.64148+00');


--
-- Data for Name: services; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.services VALUES (1, 'Đăng ký kinh doanh', 'Dịch vụ đăng ký giấy phép kinh doanh', 1, 'DKKD', 30, 100, '{"fields": [{"name": "business_name", "type": "text", "label": "Tên doanh nghiệp", "required": true}, {"name": "business_type", "type": "select", "label": "Loại hình kinh doanh", "required": true}]}', true, false, '2025-10-22 16:55:42.122933', '2025-10-22 16:55:42.122933');
INSERT INTO public.services VALUES (2, 'Nộp thuế', 'Dịch vụ nộp thuế và kê khai thuế', 2, 'NTHUE', 15, 100, '{"fields": [{"name": "tax_code", "type": "text", "label": "Mã số thuế", "required": true}, {"name": "tax_period", "type": "select", "label": "Kỳ nộp thuế", "required": true}]}', true, false, '2025-10-22 16:55:42.122933', '2025-10-22 16:55:42.122933');
INSERT INTO public.services VALUES (3, 'Cấp giấy tờ', 'Dịch vụ cấp các loại giấy tờ, chứng nhận', 3, 'CGTO', 20, 100, '{"fields": [{"name": "document_type", "type": "select", "label": "Loại giấy tờ", "required": true}, {"name": "urgent", "type": "checkbox", "label": "Xử lý khẩn cấp", "required": false}]}', true, false, '2025-10-22 16:55:42.122933', '2025-10-22 16:55:42.122933');
INSERT INTO public.services VALUES (4, 'Hỗ trợ kỹ thuật', 'Dịch vụ hỗ trợ kỹ thuật CNTT', 4, 'HTKT', 25, 100, '{"fields": [{"name": "issue_type", "type": "select", "label": "Loại vấn đề", "required": true}, {"name": "description", "type": "textarea", "label": "Mô tả chi tiết", "required": true}]}', true, false, '2025-10-22 16:55:42.122933', '2025-10-22 16:55:42.122933');
INSERT INTO public.services VALUES (5, 'Lập kế hoạch dự án', 'Hỗ trợ lập kế hoạch và quản lý dự án', 1, 'KHDA', 45, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (6, 'Báo cáo thống kê', 'Lập báo cáo và thống kê hoạt động', 1, 'BCTK', 30, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (7, 'Tư vấn quy trình', 'Tư vấn về quy trình và thủ tục hành chính', 1, 'TVQT', 25, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (8, 'Thanh toán hóa đơn', 'Xử lý thanh toán các loại hóa đơn', 2, 'TTHD', 20, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (9, 'Kế toán doanh thu', 'Quản lý và kế toán doanh thu', 2, 'KTDT', 35, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (10, 'Kiểm tra tài chính', 'Kiểm tra và đối soát tài chính', 2, 'KTTC', 40, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (11, 'Cấp phép hoạt động', 'Cấp các loại giấy phép hoạt động', 3, 'CPHD', 50, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (12, 'Quản lý nhân sự', 'Xử lý hồ sơ và quản lý nhân sự', 3, 'QLNS', 30, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (13, 'Văn thư lưu trữ', 'Quản lý văn bản và lưu trữ hồ sơ', 3, 'VTLT', 15, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (14, 'Cài đặt phần mềm', 'Hỗ trợ cài đặt và cấu hình phần mềm', 4, 'CDPM', 60, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (15, 'Bảo trì hệ thống', 'Bảo trì và nâng cấp hệ thống IT', 4, 'BTHT', 90, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');
INSERT INTO public.services VALUES (16, 'Đào tạo CNTT', 'Đào tạo sử dụng công nghệ thông tin', 4, 'DTCN', 120, 100, NULL, true, false, '2025-10-22 17:32:39.882828', '2025-10-22 17:32:39.882828');


--
-- Data for Name: queue_tickets; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.queue_tickets VALUES (127, 'B002', 'Lĩnh', '0932433459', NULL, 8, 2, 4, NULL, 'waiting', 'normal', NULL, NULL, NULL, 30, '2026-01-07 20:15:14.654094', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.queue_tickets VALUES (126, 'A001', 'Lĩnh', 'test', NULL, 1, 1, 3, NULL, 'completed', 'normal', NULL, NULL, NULL, 30, '2026-01-07 20:14:54.111162', NULL, '2026-01-07 20:15:23.918337', '2026-01-07 20:15:26.711575', '2026-01-07 20:15:26.711544', NULL, NULL, NULL, NULL, 5, 'Đánh giá 5 sao từ khách hàng', '2026-01-07 20:15:40.080402+00');


--
-- Data for Name: feedback; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: knowledge_base_categories; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: knowledge_base_articles; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: knowledge_base_attachments; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: leave_requests; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: qr_codes; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.qr_codes VALUES (1, 1, '690cb944-fd22-41b5-99b4-c31f569492c0', 'http://localhost:3000/register?dept=1&token=uuid1', true, '2025-12-31 23:59:59', '2025-10-22 16:55:42.140053', '2025-10-22 16:55:42.140053');
INSERT INTO public.qr_codes VALUES (2, 2, 'd6852a6e-58fa-4714-b115-da14c4de0e58', 'http://localhost:3000/register?dept=2&token=uuid2', true, '2025-12-31 23:59:59', '2025-10-22 16:55:42.140053', '2025-10-22 16:55:42.140053');
INSERT INTO public.qr_codes VALUES (3, 3, 'b09ee254-87d5-43d8-a969-11448550319d', 'http://localhost:3000/register?dept=3&token=uuid3', true, '2025-12-31 23:59:59', '2025-10-22 16:55:42.140053', '2025-10-22 16:55:42.140053');
INSERT INTO public.qr_codes VALUES (4, 4, '91a5007b-5591-4bd1-ba5c-845e936f23c6', 'http://localhost:3000/register?dept=4&token=uuid4', true, '2025-12-31 23:59:59', '2025-10-22 16:55:42.140053', '2025-10-22 16:55:42.140053');


--
-- Data for Name: queue_settings; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.queue_settings VALUES (1, 1, 50, false, 1.20, '{"sms": true, "push": false, "email": true}', '{}', '2025-10-22 16:55:42.142998', '2025-10-22 16:55:42.142998');
INSERT INTO public.queue_settings VALUES (2, 2, 40, false, 1.00, '{"sms": true, "push": true, "email": false}', '{}', '2025-10-22 16:55:42.142998', '2025-10-22 16:55:42.142998');
INSERT INTO public.queue_settings VALUES (3, 3, 30, false, 1.10, '{"sms": false, "push": true, "email": true}', '{}', '2025-10-22 16:55:42.142998', '2025-10-22 16:55:42.142998');
INSERT INTO public.queue_settings VALUES (4, 4, 25, false, 1.30, '{"sms": true, "push": false, "email": true}', '{}', '2025-10-22 16:55:42.142998', '2025-10-22 16:55:42.142998');


--
-- Data for Name: service_form_fields; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: service_sessions; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: shifts; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.shifts VALUES ('6906373c-f27d-435d-81a9-80a614aeabba', 'Ca Sáng', 'morning', '07:00:00', '15:00:00', NULL, true, '2026-01-07 14:00:27.353994+00', '2026-01-07 14:00:27.353994+00');
INSERT INTO public.shifts VALUES ('e2b4ea03-c2a5-4e6e-b0a3-cb567fdb9820', 'Ca Chiều', 'afternoon', '15:00:00', '23:00:00', NULL, true, '2026-01-07 14:00:27.353994+00', '2026-01-07 14:00:27.353994+00');
INSERT INTO public.shifts VALUES ('80a69d6d-2a3f-4f93-abdd-23656075424b', 'Ca Tối', 'night', '23:00:00', '07:00:00', NULL, true, '2026-01-07 14:00:27.353994+00', '2026-01-07 14:00:27.353994+00');


--
-- Data for Name: staff_schedules; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.staff_schedules VALUES ('e4005c62-db5b-4723-aabb-10624a5674fc', 3, 2, '6906373c-f27d-435d-81a9-80a614aeabba', '2026-01-07', 'scheduled', '', '2026-01-07 16:39:59.28191+00', '2026-01-07 16:39:59.28191+00');
INSERT INTO public.staff_schedules VALUES ('e47692bf-5776-424b-9c60-c51cef601efd', 6, 2, 'e2b4ea03-c2a5-4e6e-b0a3-cb567fdb9820', '2026-01-07', 'scheduled', '', '2026-01-07 16:43:18.697274+00', '2026-01-07 16:43:18.697274+00');
INSERT INTO public.staff_schedules VALUES ('1abc454e-d031-4433-a2e2-ddc1e4f445af', 3, 2, 'e2b4ea03-c2a5-4e6e-b0a3-cb567fdb9820', '2026-01-06', 'scheduled', '', '2026-01-07 16:45:38.387504+00', '2026-01-07 16:45:38.387504+00');


--
-- Data for Name: shift_exchanges; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: staff_attendance; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: staff_checkins; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: staff_notifications; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: staff_performance; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.staff_performance VALUES (1, 3, 1, '2025-10-22', 2, 25.50, 10, 2, 5.00, '2025-10-22 16:55:42.136843', '2025-10-22 16:55:42.136843');
INSERT INTO public.staff_performance VALUES (2, 4, 2, '2025-10-22', 1, 15.00, 4, 1, 4.00, '2025-10-22 16:55:42.136843', '2025-10-22 16:55:42.136843');
INSERT INTO public.staff_performance VALUES (3, 5, 3, '2025-10-22', 0, 0.00, 0, 0, 0.00, '2025-10-22 16:55:42.136843', '2025-10-22 16:55:42.136843');


--
-- Data for Name: staff_settings; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: ticket_complaints; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.ticket_complaints VALUES (60, 126, 'Lĩnh', NULL, NULL, 'Nhân viên không nhiệt tình', NULL, 'waiting', NULL, NULL, '2026-01-07 20:15:40.09305', NULL);


--
-- Name: activity_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.activity_logs_id_seq', 1, false);


--
-- Name: ai_conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.ai_conversations_id_seq', 86, true);


--
-- Name: announcements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.announcements_id_seq', 2, true);


--
-- Name: counters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.counters_id_seq', 5, true);


--
-- Name: daily_login_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.daily_login_logs_id_seq', 10, true);


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.departments_id_seq', 4, true);


--
-- Name: feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.feedback_id_seq', 1, false);


--
-- Name: knowledge_base_articles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.knowledge_base_articles_id_seq', 1, false);


--
-- Name: knowledge_base_attachments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.knowledge_base_attachments_id_seq', 1, false);


--
-- Name: knowledge_base_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.knowledge_base_categories_id_seq', 1, false);


--
-- Name: qr_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.qr_codes_id_seq', 4, true);


--
-- Name: queue_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.queue_settings_id_seq', 4, true);


--
-- Name: queue_tickets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.queue_tickets_id_seq', 127, true);


--
-- Name: service_form_fields_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.service_form_fields_id_seq', 1, false);


--
-- Name: service_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.service_sessions_id_seq', 1, false);


--
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.services_id_seq', 16, true);


--
-- Name: staff_notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.staff_notifications_id_seq', 6, true);


--
-- Name: staff_performance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.staff_performance_id_seq', 3, true);


--
-- Name: staff_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.staff_settings_id_seq', 1, false);


--
-- Name: ticket_complaints_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.ticket_complaints_id_seq', 60, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

\unrestrict Y8CSghmeo8CWcN45shvkC6on7PASl3ntkMxBcXG2TZFG9aZmpiZoMhwYvVE5oSN

