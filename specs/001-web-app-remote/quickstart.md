# Quickstart Guide: Claude Code Remote Web Controller

**Created**: 2025-10-13
**Purpose**: Step-by-step guide to set up, develop, and test the application

## Prerequisites

**Required Software**:
- Node.js 18+ and npm/pnpm
- Python 3.11+
- uv (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker and Docker Compose
- Claude Code CLI installed and accessible in PATH
- Git

**Development Environment**:
- VS Code or preferred editor
- Terminal access
- Minimum 4GB RAM available
- PostgreSQL client (optional, for DB inspection)

---

## Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Clone repository
git checkout 001-web-app-remote

# Create environment files
cp .env.example .env

# Edit .env with your settings
# Required: JWT_SECRET, DATABASE_URL
```

### 2. Start Infrastructure

```bash
# Start PostgreSQL with Docker Compose
docker-compose up -d postgres

# Wait for database to be ready
docker-compose logs -f postgres  # Ctrl+C when you see "database system is ready"
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment and install dependencies with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn src.main:app --reload --port 8000
```

Backend will be available at `http://localhost:8000`

### 4. Setup Frontend (in new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 5. Test the Application

1. Open browser to `http://localhost:5173`
2. Register a new account
3. Create a new session
4. Connect to Claude Code
5. Send a test command: "What files are in the current directory?"

---

## Detailed Development Setup

### Backend Setup

#### 1. Environment Configuration

Create `backend/.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:5432/claude_remote

# Authentication
JWT_SECRET=your-secret-key-min-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Claude Code
CLAUDE_CODE_PATH=/path/to/claude  # Leave empty to use PATH
CLAUDE_CODE_TIMEOUT=300

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### 2. Database Setup

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Create database (if not exists)
docker-compose exec postgres createdb -U admin claude_remote

# Initialize Alembic (one-time setup)
cd backend
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

#### 3. Install Dependencies

```bash
cd backend

# Install with uv (recommended)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

**pyproject.toml dependencies**:
```toml
[project]
name = "claude-remote-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.12.0",
    "pydantic>=2.4.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.6",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.25.0",
    "ruff>=0.1.0",
    "mypy>=1.6.0",
]
```

#### 4. Run Backend

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 5. Verify Backend

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

---

### Frontend Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

**package.json dependencies**:
```json
{
  "dependencies": {
    "vue": "^3.3.8",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "pinia-plugin-persistedstate": "^3.2.0",
    "axios": "^1.6.0",
    "@vueuse/core": "^10.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.5.0",
    "vite": "^5.0.0",
    "typescript": "^5.2.2",
    "vue-tsc": "^1.8.22",
    "tailwindcss": "^3.3.5",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "vitest": "^1.0.0",
    "@vue/test-utils": "^2.4.1",
    "playwright": "^1.40.0",
    "eslint": "^8.54.0",
    "@typescript-eslint/eslint-plugin": "^6.12.0",
    "@typescript-eslint/parser": "^6.12.0"
  }
}
```

#### 2. Initialize Shadcn Vue

```bash
cd frontend

# Initialize shadcn-vue
npx shadcn-vue@latest init

# Add required components
npx shadcn-vue@latest add button input card scroll-area dialog alert badge
```

#### 3. Configure Environment

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

#### 4. Run Frontend

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

#### 5. Verify Frontend

Open `http://localhost:5173` in browser.

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_auth_service.py

# Run integration tests only
pytest tests/integration/

# Run with verbose output
pytest -v -s
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test

# Run unit tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests in headed mode (see browser)
npm run test:e2e:headed
```

### Contract Tests

```bash
# Test WebSocket protocol compliance
pytest backend/tests/contract/test_websocket_protocol.py

# Test REST API contract
pytest backend/tests/contract/test_rest_api.py
```

---

## Database Management

### Migrations

```bash
cd backend

# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Show migration history
alembic history

# Show current version
alembic current
```

### Database Access

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U admin -d claude_remote

# Useful queries
\dt                    # List tables
\d users               # Describe users table
SELECT * FROM sessions WHERE status = 'ACTIVE';
```

### Database Reset (Development Only)

```bash
# Drop and recreate database
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

---

## Common Development Workflows

### Workflow 1: Add New REST API Endpoint

1. **Define route** in `backend/src/api/[module].py`
2. **Create Pydantic schema** in `backend/src/schemas/[module].py`
3. **Add business logic** in `backend/src/services/[module].py`
4. **Write tests** in `backend/tests/unit/test_[module].py`
5. **Update contract** in `specs/001-web-app-remote/contracts/rest-api.md`
6. **Run tests**: `pytest -v`
7. **Test manually** via Swagger UI at `/docs`

### Workflow 2: Add New Vue Component

1. **Create component** in `frontend/src/components/[Component].vue`
2. **Define TypeScript types** in `frontend/src/types/[module].ts`
3. **Write unit test** in `frontend/tests/unit/[Component].spec.ts`
4. **Use component** in parent view
5. **Run tests**: `npm run test`
6. **View in browser**: `npm run dev`

### Workflow 3: Modify WebSocket Protocol

1. **Update contract** in `specs/001-web-app-remote/contracts/websocket-protocol.md`
2. **Update backend handler** in `backend/src/api/websocket.py`
3. **Update frontend composable** in `frontend/src/composables/useWebSocket.ts`
4. **Update TypeScript types** in `frontend/src/types/message.ts`
5. **Write contract tests** for both backend and frontend
6. **Test end-to-end** with real WebSocket connection

### Workflow 4: Modify Database Schema

1. **Update SQLAlchemy models** in `backend/src/models/[model].py`
2. **Generate migration**: `alembic revision --autogenerate -m "Description"`
3. **Review migration** in `backend/alembic/versions/[hash]_description.py`
4. **Apply migration**: `alembic upgrade head`
5. **Update Pydantic schemas** if needed
6. **Update frontend types** if needed
7. **Run tests** to ensure compatibility

---

## Debugging

### Backend Debugging

**VS Code launch.json**:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

**Enable debug logging**:
```python
# backend/src/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Frontend Debugging

**Vue DevTools**: Install browser extension for Vue 3

**Console Logging**:
```typescript
// Enable Pinia devtools
const pinia = createPinia()
pinia.use(() => ({ $subscribe: () => console.log('State changed') }))
```

**WebSocket Debugging**:
```typescript
// frontend/src/composables/useWebSocket.ts
const ws = new WebSocket(url)
ws.addEventListener('message', (event) => {
  console.log('[WS] Received:', event.data)
})
ws.addEventListener('error', (error) => {
  console.error('[WS] Error:', error)
})
```

### Database Debugging

**Enable SQL logging**:
```python
# backend/src/config.py
engine = create_async_engine(
    DATABASE_URL,
    echo=True  # Log all SQL queries
)
```

---

## Production Deployment

### Build for Production

```bash
# Frontend
cd frontend
npm run build
# Output in frontend/dist/

# Backend
cd backend
uv pip install --no-dev  # Install production dependencies only
```

### Docker Deployment

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**docker-compose.yml** (production-ready):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres/${POSTGRES_DB}
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      - postgres
    ports:
      - "8000:8000"
    networks:
      - app-network

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```

---

## Troubleshooting

### Backend Won't Start

**Symptom**: `uvicorn` crashes or refuses connections

**Solutions**:
1. Check DATABASE_URL is correct: `echo $DATABASE_URL`
2. Verify PostgreSQL is running: `docker-compose ps`
3. Check migrations are applied: `alembic current`
4. Review logs for errors: `docker-compose logs postgres`
5. Test database connection: `psql $DATABASE_URL`

### Frontend Can't Connect to Backend

**Symptom**: Network errors in browser console

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check VITE_API_URL in `.env` matches backend URL
3. Verify CORS configuration in `backend/src/main.py`
4. Check browser network tab for detailed error

### WebSocket Connection Fails

**Symptom**: "WebSocket connection failed" error

**Solutions**:
1. Verify JWT token is valid and not expired
2. Check WebSocket URL format: `ws://` not `http://`
3. Ensure session_id exists and belongs to authenticated user
4. Check firewall/proxy allows WebSocket connections
5. Review backend logs for connection errors

### Claude Code Process Won't Start

**Symptom**: Session stuck in "CONNECTING" status

**Solutions**:
1. Verify Claude Code CLI is installed: `which claude`
2. Check working directory exists and is accessible
3. Review stderr output in backend logs
4. Test Claude Code manually: `claude --help`
5. Check subprocess spawning permissions

### Database Migration Fails

**Symptom**: `alembic upgrade head` errors

**Solutions**:
1. Check current migration version: `alembic current`
2. Review migration file for errors
3. Manually fix database schema if needed
4. Reset migrations (development only): `alembic downgrade base && alembic upgrade head`
5. Regenerate migration: `alembic revision --autogenerate -m "Fixed migration"`

---

## Performance Optimization

### Backend Optimization

1. **Connection Pooling**: Configure SQLAlchemy pool size
   ```python
   engine = create_async_engine(url, pool_size=20, max_overflow=10)
   ```

2. **Query Optimization**: Add indexes for frequently queried fields
   ```sql
   CREATE INDEX idx_sessions_last_activity ON sessions(last_activity);
   ```

3. **Async Processing**: Use background tasks for non-critical operations
   ```python
   background_tasks.add_task(cleanup_old_sessions)
   ```

### Frontend Optimization

1. **Code Splitting**: Lazy load routes
   ```typescript
   const HomeView = () => import('./views/HomeView.vue')
   ```

2. **Virtual Scrolling**: For long message lists
   ```vue
   <RecycleScroller :items="messages" :item-size="50" />
   ```

3. **Debounce Input**: Reduce API calls
   ```typescript
   const debouncedSearch = useDebounceFn(searchSessions, 300)
   ```

---

## Security Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **JWT Secrets**: Use strong, random 32+ character secrets
3. **Password Hashing**: Bcrypt with 12+ rounds (already configured)
4. **Input Validation**: Always validate user input on backend
5. **Rate Limiting**: Enforced at API level
6. **CORS**: Restrict to specific frontend origin in production
7. **HTTPS**: Use TLS in production (configure reverse proxy)
8. **SQL Injection**: Use SQLAlchemy parameterized queries (already safe)

---

## Summary

**Setup Time**: ~15 minutes
**Key Commands**:
- Backend: `uvicorn src.main:app --reload`
- Frontend: `npm run dev`
- Tests: `pytest` (backend), `npm run test` (frontend)
- Database: `alembic upgrade head`

**Ready for Development**: ✅
**Next Step**: Run `/speckit.tasks` to generate implementation task list
