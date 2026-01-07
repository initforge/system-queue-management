# Technical Documentation - Queue Management System

## Overview
A government service queue management system built with FastAPI backend and React frontend.

## Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Frontend   │◄──►│   Backend   │◄──►│  Database   │
│   React     │    │   FastAPI   │    │  PostgreSQL │
│  Port 3000  │    │  Port 8000  │    │  Port 5433  │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │    Redis    │
                   │  Port 6379  │
                   └─────────────┘
```

## Docker Commands
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Access database
docker exec -it queue_db psql -U admin -d queue_managment

# Restart backend
docker compose restart backend
```

## API Routes
| Prefix | Description |
|--------|-------------|
| `/api/v1/auth` | Login, logout |
| `/api/v1/staff` | Staff dashboard, queue operations |
| `/api/v1/manager` | Manager dashboard, staff management |
| `/api/v1/schedule` | Schedule management |
| `/api/v1/ai-helper` | AI assistant (Gemini) |
| `/api/v1/tickets` | Ticket registration, status |
| `/api/v1/departments` | Department and service listing |

## Frontend Modules
| Path | Description |
|------|-------------|
| `/` | Homepage, public queue display |
| `/login` | Staff/Manager login |
| `/staff` | Staff dashboard |
| `/manager` | Manager dashboard |
| `/service-registration` | Customer ticket registration |
| `/waiting/:id` | Customer waiting page |
| `/review/:id` | Customer feedback page |

## Environment Variables
Set in `docker-compose.yml` or `.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `REACT_APP_API_URL` - Backend API URL for frontend

## User Accounts (Default)
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@qstream.vn | Admin123! |
| Manager | manager.01@qstream.vn | Admin123! |
| Staff | staff.01@qstream.vn | Admin123! |
