# Deployment Guide - Claude Code Remote Web Controller

## Prerequisites

### System Requirements
- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL 15+
- Docker & Docker Compose (optional, recommended)

### Environment Setup

#### 1. Database Setup
```bash
# Start PostgreSQL (via docker-compose or local installation)
docker-compose up -d postgres

# Run database migrations
cd backend
alembic upgrade head

# Verify migration completed
alembic current
```

#### 2. Backend Environment
```bash
cd backend
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - DATABASE_URL=postgresql://admin:password@localhost:5432/claude_remote
# - JWT_SECRET=<generate-secure-key>
# - CLAUDE_CODE_PATH=/usr/local/bin/claude  # Path to Claude Code binary
```

#### 3. Frontend Environment
```bash
cd frontend
cp .env.example .env

# Edit .env with your configuration
# Required variables:
# - VITE_API_URL=http://localhost:8000/api/v1
# - VITE_WS_URL=ws://localhost:8000/ws
```

## Installation

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

This will:
- Start PostgreSQL database
- Build and run backend API (Port 8000)
- Build and run frontend app (Port 5173)

### Manual Installation

**Backend:**
```bash
cd backend
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .
uvicorn src.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Deployment Checklist

### Pre-Deployment Verification

- [ ] **T017**: Database migration applied successfully
  ```bash
  alembic current  # Should show migration version
  ```

- [ ] **Security**:
  - [ ] JWT_SECRET set to secure random value
  - [ ] CORS_ORIGINS configured for target domain
  - [ ] Rate limiting middleware active (10 commands/min per user)
  - [ ] HTTPS enabled in production
  - [ ] Security logging configured

- [ ] **Core Features Verified**:
  - [ ] User registration and login working
  - [ ] WebSocket connection stable
  - [ ] Command execution and streaming functional
  - [ ] File viewing with path validation working
  - [ ] Tool approval prompts showing correctly

- [ ] **User Story Coverage**:
  - [ ] ✅ US1: Remote command execution (Complete)
  - [ ] ✅ US2: Real-time streaming (Complete)
  - [ ] ✅ US3: Session persistence & reconnection (Complete)
  - [ ] ✅ US4: File and tool interaction (Complete)
  - [ ] ✅ US5: Multi-device security (Complete - backend)

### Production Deployment

#### 1. Build Frontend
```bash
cd frontend
npm run build
# Output in: frontend/dist/
```

#### 2. Configure Backend for Production
```bash
# backend/.env
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS="https://yourdomain.com"
```

#### 3. Run with Production Server
```bash
# Using gunicorn + uvicorn workers
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

#### 4. Reverse Proxy (Nginx)
```nginx
upstream backend {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # Frontend static files
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API routes
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket routes
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Post-Deployment

### Monitoring

- **Application Logs**: Check `/var/log/claude-remote/` for errors
- **Database Health**: Monitor PostgreSQL connection pool
- **Rate Limiting**: Monitor `X-RateLimit-*` headers in responses
- **WebSocket Uptime**: Monitor 99% uptime target

### Performance Targets

- Command execution: <2 seconds initial response
- Real-time streaming: <500ms latency per chunk
- WebSocket connection: 99% uptime during 8-hour sessions
- Page load: <3 seconds on standard broadband

## Rollback Plan

If issues occur during deployment:

```bash
# Revert database migration
alembic downgrade -1

# Revert to previous backend version
git checkout <previous-commit>

# Clear frontend cache
rm -rf frontend/dist
npm run build  # Rebuild with previous version
```

## Support

For issues or questions:
- Check application logs in `backend/logs/`
- Review database migration status: `alembic current`
- Verify all environment variables set: `env | grep CLAUDE`
