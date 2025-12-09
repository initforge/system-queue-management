# Cloudinary Setup Guide

## Cách 1: Sử dụng .env file (Khuyến nghị)

1. Tạo file `.env` trong thư mục `queue-management-system/`:
```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

2. Docker Compose sẽ tự động đọc từ `.env` file

3. Restart container:
```bash
docker-compose restart backend
```

## Cách 2: Set trực tiếp trong docker-compose.yml

Sửa file `docker-compose.yml`, thay thế `${CLOUDINARY_CLOUD_NAME:-}` bằng giá trị thực:

```yaml
environment:
  - CLOUDINARY_CLOUD_NAME=your_cloud_name
  - CLOUDINARY_API_KEY=your_api_key
  - CLOUDINARY_API_SECRET=your_api_secret
```

Sau đó restart:
```bash
docker-compose restart backend
```

## Cách 3: Set environment variables trước khi chạy docker-compose

```bash
export CLOUDINARY_CLOUD_NAME=your_cloud_name
export CLOUDINARY_API_KEY=your_api_key
export CLOUDINARY_API_SECRET=your_api_secret
docker-compose restart backend
```

## Lấy Cloudinary Credentials

1. Đăng ký tài khoản tại: https://cloudinary.com/users/register/free
2. Vào Dashboard: https://cloudinary.com/console
3. Copy các giá trị:
   - **Cloud Name**: Tên cloud của bạn
   - **API Key**: Key từ dashboard
   - **API Secret**: Secret từ dashboard

## Kiểm tra Cloudinary đã hoạt động

Sau khi set credentials và restart, kiểm tra logs:
```bash
docker logs queue_backend | grep -i cloudinary
```

Bạn sẽ thấy:
- ✅ `Cloudinary service initialized successfully` - Thành công
- ❌ `Cloudinary credentials not configured` - Chưa set credentials

## Test Upload

Sau khi setup xong, bạn có thể test upload file qua Knowledge Base API:
- Endpoint: `POST /api/v1/knowledge-base/articles/{article_id}/upload`
- Upload file sẽ được lưu trên Cloudinary
