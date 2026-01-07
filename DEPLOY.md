# 🚀 Deploy QStream to DigitalOcean App Platform

## Prerequisites
- GitHub repository: `initforge/system-queue-management`
- DigitalOcean account with billing enabled

## Step-by-Step Deployment

### Step 1: Create App on DigitalOcean
1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click **Create App**
3. Select **GitHub** as source
4. Authorize and select repo: `initforge/system-queue-management`
5. Select branch: `main`

### Step 2: Configure Resources
App Platform sẽ tự detect các services từ Dockerfiles. Bạn cần configure:

#### A. Database (PostgreSQL)
- Click **Add Resource** → **Database**
- Engine: PostgreSQL 15
- Size: Basic ($7/month) hoặc Dev ($0 - for testing)

#### B. Backend Service
- Name: `backend`
- Source Directory: `/backend`
- Dockerfile Path: `backend/Dockerfile`
- HTTP Port: `8000`
- Instance Size: Basic XXS ($5/month)

**Environment Variables (RUN_TIME):**
```
DATABASE_URL = ${db.DATABASE_URL}    # Auto-linked from DB
JWT_SECRET_KEY = <generate-secure-key>  # openssl rand -hex 32
JWT_ALGORITHM = HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
ENVIRONMENT = production
DEBUG = false
CORS_ORIGINS = https://${APP_DOMAIN}
```

**Routes:**
- `/api` → backend
- `/ws` → backend (for WebSocket)

#### C. Frontend Service  
- Name: `frontend`
- Source Directory: `/frontend`
- Dockerfile Path: `frontend/Dockerfile`
- HTTP Port: `80`
- Instance Size: Basic XXS ($5/month)

**Environment Variables (BUILD_TIME):**
```
REACT_APP_API_URL = https://${APP_DOMAIN}/api/v1
REACT_APP_WS_URL = wss://${APP_DOMAIN}/ws
```

**Routes:**
- `/` → frontend (catch-all)

### Step 3: Database Initialization
App Platform's PostgreSQL KHÔNG tự chạy migration. Bạn cần:

1. Sau khi deploy xong, vào **Database** → **Connection Details**
2. Copy connection string
3. Chạy migration từ local:
```bash
# Export connection string
export DATABASE_URL="postgresql://user:pass@host:port/db?sslmode=require"

# Run migrations (hoặc connect direct và run SQL)
psql $DATABASE_URL < database/schema.sql
psql $DATABASE_URL < database/data.sql
```

Hoặc dùng App Platform Console:
```bash
doctl apps console <app-id>
```

### Step 4: Final Configuration
1. **Custom Domain** (optional): Add your domain in App Settings
2. **SSL**: Auto-configured by DigitalOcean
3. **Health Check**: Already configured at `/api/v1/health`

## Estimated Monthly Cost
| Service | Size | Cost |
|---------|------|------|
| Database (PostgreSQL) | Dev | $0 (or $7 Basic) |
| Backend | Basic XXS | $5 |
| Frontend | Basic XXS | $5 |
| **Total** | | **$10-17/month** |

## Troubleshooting

### Build Failed
- Check Dockerfile syntax
- Ensure all files are committed to git
- Check build logs in App Platform

### Database Connection Error
- Verify DATABASE_URL uses `${db.DATABASE_URL}` syntax
- Check database is in same region as app
- SSL mode should be `require` for managed DB

### WebSocket Not Working
- Ensure backend route includes `/ws`
- Check CORS_ORIGINS includes your domain
- WebSocket URL must use `wss://` in production

### Frontend Can't Connect to API
- Verify REACT_APP_API_URL is set as BUILD_TIME variable
- Must use `https://` in production
- Check browser console for CORS errors

## Local Production Testing
```bash
# Copy and edit environment
cp .env.example .env
# Edit .env with your values

# Build and run production
docker-compose -f docker-compose.prod.yml up --build
```
