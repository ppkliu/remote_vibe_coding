# MVP Deployment Guide: Claude Code Remote Web Controller

## Overview

This guide walks you through deploying the MVP (Minimum Viable Product) of the Claude Code Remote Web Controller. The MVP includes all core features needed for remote command execution, real-time streaming, and session management.

**Status**: 72.67% of features complete (109/150 tasks)
**MVP Ready**: YES ✅

---

## Prerequisites

### System Requirements
- **Docker & Docker Compose**: v20.10+ 
- **Port Availability**: 5432 (PostgreSQL), 8000 (Backend), 5173 (Frontend)
- **Disk Space**: ~2GB for images and data
- **Memory**: 2GB minimum recommended

### Software
- Docker Desktop or Docker Engine
- docker-compose CLI

---

## Quick Start (5 minutes)

### 1. Clone & Navigate
```bash
cd /path/to/remote_vibe_coding
```

### 2. Create Environment Files
```bash
# Backend
cp backend/.env.example backend/.env
# Update JWT_SECRET if desired (optional for local dev)

# Frontend  
cp frontend/.env.example frontend/.env
# Default values should work for local deployment
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Verify Deployment
```bash
# Check all services running
docker-compose ps

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1
- **API Docs**: http://localhost:8000/docs

---

## Detailed Setup

### Step 1: Environment Configuration

**Backend (.env)**
```env
DATABASE_URL=postgresql+asyncpg://admin:password@postgres/claude_remote
JWT_SECRET=your-secret-key-min-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=false
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost
CLAUDE_CODE_PATH=claude
```

**Frontend (.env.local)**
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

### Step 2: Docker Compose Startup

```bash
# Start all services
docker-compose up -d

# Wait for PostgreSQL to be ready (30-60 seconds)
docker-compose exec postgres pg_isready -U admin

# Apply database migrations (automatic on backend start)
docker-compose logs backend | grep "Running upgrade"
```

### Step 3: Verify Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U admin -d claude_remote

# Check tables
\dt

# Verify migration was applied
SELECT * FROM alembic_version;
```

### Step 4: Test Endpoints

**Health Check**
```bash
curl http://localhost:8000/health
# Response: {"status": "healthy", "service": "claude-remote-backend"}
```

**Register New User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!"
  }'
```

**Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Password123!"
  }'
# Response includes access_token and refresh_token
```

---

## MVP Features

### ✅ Available Features

| Feature | Status | Notes |
|---------|--------|-------|
| User Registration | ✅ Ready | Secure password hashing with bcrypt |
| User Login | ✅ Ready | JWT token-based authentication |
| Create Session | ✅ Ready | Multi-session per user |
| List Sessions | ✅ Ready | Paginated response |
| Remote Command Execution | ✅ Ready | Via WebSocket connection |
| Real-time Output Streaming | ✅ Ready | Chunked delivery with sequence numbers |
| Session Persistence | ✅ Ready | Survives connection drops |
| Auto Reconnection | ✅ Ready | Exponential backoff (1s, 2s, 4s, 8s, 30s) |
| Rate Limiting | ✅ Ready | 10 commands/min per user |
| Multi-device Access | ✅ Ready | Same session across devices |

### ⚠️ Not in MVP

- Tool approval UI (backend ready, frontend integration pending)
- Syntax highlighting
- Markdown rendering
- Copy-to-clipboard
- Full test suite
- E2E tests

---

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│        Docker Compose Network           │
├─────────────────────────────────────────┤
│                                         │
│  ┌───────────────┐  ┌──────────────┐  │
│  │   Frontend    │  │   Backend    │  │
│  │  (Vite/Vue3)  │  │  (FastAPI)   │  │
│  │ :5173         │  │  :8000       │  │
│  └───────────────┘  └──────────────┘  │
│         │                    │         │
│         └────────┬───────────┘         │
│                  │                     │
│          ┌───────▼─────────┐           │
│          │   PostgreSQL    │           │
│          │   :5432         │           │
│          │ claude_remote   │           │
│          └─────────────────┘           │
│                                         │
└─────────────────────────────────────────┘
```

---

## Usage Guide

### 1. Open Application
Navigate to http://localhost:5173

### 2. Register Account
- Click "Register"
- Enter username, email, password
- Click "Sign Up"

### 3. Create Session
- Click "New Session"
- Confirm Claude Code process starts
- Wait for "Ready" status

### 4. Send Commands
- Type command in input box
- Press Enter
- Watch real-time output stream

### 5. Manage Sessions
- View all sessions
- Resume previous sessions
- View message history

---

## Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i :5173  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Or use different ports in docker-compose.yml
```

### PostgreSQL Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Backend Won't Start
```bash
# Check Python dependencies
docker-compose logs backend

# Rebuild backend image
docker-compose build --no-cache backend

# Restart
docker-compose up -d backend
```

### Frontend Not Loading
```bash
# Check Vite dev server
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend

# Restart
docker-compose up -d frontend
```

### JWT Token Expired
Simply log out and log back in to get a fresh token.

### Rate Limit Hit
Wait 1 minute (window resets per minute) or send fewer commands.

---

## Monitoring & Debugging

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Database Access
```bash
docker-compose exec postgres psql -U admin -d claude_remote
```

### Backend API Docs
Open http://localhost:8000/docs (Swagger UI)

### Check Health
```bash
curl http://localhost:8000/health
```

---

## Performance Tuning

### For Production Use

1. **Set DEBUG=false** in backend .env
2. **Increase JWT_EXPIRY** if needed
3. **Update CORS_ORIGINS** to production domain
4. **Use strong JWT_SECRET** (min 32 chars, random)
5. **Consider database backups** (PostgreSQL volume)

### Database Performance
- Indexes already configured
- Connection pooling enabled
- Async queries throughout

---

## Security Checklist

- [ ] Changed JWT_SECRET to random value
- [ ] Updated CORS_ORIGINS for production domain
- [ ] Database credentials changed from defaults
- [ ] PostgreSQL volume mounted to persistent storage
- [ ] Firewall restricts access to necessary ports only
- [ ] HTTPS configured (reverse proxy recommended)
- [ ] Rate limiting adequate for use case

---

## Cleanup

### Stop Services
```bash
docker-compose down
```

### Stop & Remove Data
```bash
docker-compose down -v  # -v removes named volumes
```

### Remove Everything
```bash
docker-compose down -v --remove-orphans
docker system prune -a
```

---

## Next Steps

### Post-MVP Enhancements
1. User Story 4 Frontend Integration (Tool Approvals UI)
2. Enhanced Error Handling & Toast Notifications
3. Syntax Highlighting & Markdown Rendering
4. Full Test Suite (Unit, Integration, E2E)
5. Performance Optimization
6. Production Hardening

---

## Support

### Common Issues
- Check logs: `docker-compose logs -f`
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Feature Status
See IMPLEMENTATION_STATUS.md for detailed task completion

---

## License & Attribution

Generated with Claude Code
Date: 2025-10-20

