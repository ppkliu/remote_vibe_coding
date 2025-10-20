# Development Quick Start Guide

**For**: Developers contributing to Claude Code Remote Web Controller  
**Time to setup**: ~15 minutes (with dependencies installed)  
**Last updated**: 2025-10-20

---

## Prerequisites

### Required
- **Python 3.12+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **PostgreSQL 15** - Database (via Docker recommended)
- **Git** - Version control

### Optional but Recommended
- **Docker & Docker Compose** - For PostgreSQL and services
- **VS Code** with extensions:
  - Python
  - Volar (Vue 3)
  - Tailwind CSS IntelliSense
- **Postman** or **REST Client** - API testing
- **DBeaver** - Database inspection

---

## Option A: Local Development (Recommended)

### 1. Clone Repository
```bash
git clone <repo-url>
cd remote_vibe_coding
git checkout 001-web-app-remote
```

### 2. Start Database (Docker)
```bash
# Start only PostgreSQL (not backend/frontend)
docker-compose up -d postgres

# Verify connection
docker-compose exec postgres psql -U admin -d claude_remote -c "SELECT version();"
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # Or use pyproject.toml

# Apply migrations
PYTHONPATH=. python -m alembic upgrade head

# Start backend dev server
python src/main.py
# or
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs at**: http://localhost:8000

### 4. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install
# or
pnpm install

# Start dev server
npm run dev
# or
pnpm dev
```

**Frontend runs at**: http://localhost:5173

### 5. Verify Setup

```bash
# Backend health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Frontend
open http://localhost:5173
```

---

## Option B: Docker Development

### 1. Start All Services
```bash
docker-compose up -d

# Watch logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 2. Apply Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### 3. Access Services
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### 4. Rebuild on Changes
```bash
# Backend code changes (auto-reload)
docker-compose up -d backend

# Frontend code changes (auto-reload)
docker-compose up -d frontend

# Full rebuild
docker-compose up -d --build
```

---

## Project Structure

### Backend
```
backend/
├── src/
│   ├── api/
│   │   ├── auth.py         # Auth endpoints
│   │   ├── sessions.py     # Session endpoints
│   │   ├── websocket.py    # WebSocket handler
│   │   ├── files.py        # File viewer
│   │   └── dependencies.py # DI & auth checks
│   ├── services/
│   │   ├── auth_service.py      # JWT, password hashing
│   │   ├── session_manager.py   # Session lifecycle
│   │   └── claude_bridge.py     # Claude process mgmt
│   ├── models/             # SQLAlchemy ORM
│   ├── schemas/            # Pydantic validation
│   ├── middleware/         # Rate limiting, etc
│   ├── config.py           # Settings
│   └── main.py             # FastAPI app
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── alembic/                # Database migrations
├── pyproject.toml          # Dependencies
└── requirements.txt        # (if using pip)

```

### Frontend
```
frontend/
├── src/
│   ├── views/
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   ├── HomeView.vue
│   │   └── SessionsView.vue
│   ├── components/
│   │   ├── CommandInput.vue
│   │   ├── OutputDisplay.vue
│   │   ├── ConnectionStatus.vue
│   │   ├── ToolApprovalDialog.vue
│   │   └── FileViewer.vue
│   ├── stores/             # Pinia state management
│   │   ├── auth.ts
│   │   ├── session.ts
│   │   ├── messages.ts
│   │   └── connection.ts
│   ├── services/
│   │   ├── api.ts          # Axios HTTP client
│   │   └── websocket.ts    # WebSocket client
│   ├── composables/        # Reusable logic
│   ├── types/              # TypeScript types
│   ├── router/             # Vue Router
│   ├── main.ts             # Entry point
│   └── App.vue             # Root component
├── tests/
│   ├── unit/
│   └── e2e/
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

---

## Common Development Tasks

### Running Tests

**Backend (pytest)**
```bash
cd backend
pytest tests/                          # All tests
pytest tests/unit/                     # Unit only
pytest tests/integration/              # Integration only
pytest -v --cov=src                   # With coverage
```

**Frontend (Vitest)**
```bash
cd frontend
npm run test                           # Run tests
npm run test:watch                     # Watch mode
npm run test:coverage                  # With coverage
```

### Database Operations

**Create migration**
```bash
cd backend
PYTHONPATH=. alembic revision --autogenerate -m "description"
```

**Apply migrations**
```bash
cd backend
PYTHONPATH=. alembic upgrade head     # Latest
PYTHONPATH=. alembic downgrade -1     # Previous
```

**Access database**
```bash
docker-compose exec postgres psql -U admin -d claude_remote
```

### Linting & Formatting

**Backend**
```bash
cd backend
ruff check .                    # Lint
ruff format .                   # Format
black . --check                # Alternative format check
mypy src/                       # Type checking
```

**Frontend**
```bash
cd frontend
npm run lint                    # ESLint
npm run format                  # Prettier
```

### API Testing

**With cURL**
```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"dev","email":"dev@test.com","password":"Test123!"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dev","password":"Test123!"}'

# Create session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Dev Session"}'
```

**With REST Client (VS Code)**
Create `.http` file:
```http
@baseUrl = http://localhost:8000/api/v1
@token = your_jwt_token_here

### Register
POST {{baseUrl}}/auth/register
Content-Type: application/json

{
  "username": "dev",
  "email": "dev@test.com",
  "password": "Test123!"
}

### Login
POST {{baseUrl}}/auth/login
Content-Type: application/json

{
  "username": "dev",
  "password": "Test123!"
}

### List Sessions
GET {{baseUrl}}/sessions
Authorization: Bearer {{token}}
```

---

## Debugging

### Backend Debugging

**VS Code - Python**

Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.main:app", "--reload"],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

Then press F5 to debug.

**Print debugging**
```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
```

**Database inspection**
```bash
docker-compose exec postgres psql -U admin -d claude_remote
\dt                    # List tables
\d users              # Show schema
SELECT * FROM users;  # Query data
```

### Frontend Debugging

**Vue DevTools**
- Install extension: Chrome/Firefox
- Open DevTools (F12)
- Find "Vue" tab
- Inspect components, stores, routes

**Console logging**
```typescript
console.log('Debug:', data)
console.warn('Warning:', error)
console.error('Error:', error)
```

**Network inspection**
- Open DevTools (F12)
- Go to Network tab
- Send command
- Inspect WebSocket frames in "WS" filter

### Common Issues

**Port already in use**
```bash
# Find process using port
lsof -i :8000
lsof -i :5173
lsof -i :5432

# Kill process
kill -9 <PID>
```

**Module not found (Python)**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check PYTHONPATH
export PYTHONPATH=/path/to/backend:$PYTHONPATH
```

**Dependencies mismatch (npm)**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Database connection refused**
```bash
# Start PostgreSQL
docker-compose up -d postgres
docker-compose exec postgres pg_isready -U admin
```

---

## Git Workflow

### Branches
- `main` - Production-ready
- `001-web-app-remote` - Development branch
- `feature/*` - Feature branches
- `fix/*` - Bug fix branches

### Commit Convention
```bash
# Feature
git commit -m "feat: add tool approval UI (T113-T117)"

# Bug fix
git commit -m "fix: correct WebSocket reconnection logic"

# Documentation
git commit -m "docs: add development guide"

# Refactor
git commit -m "refactor: simplify message handling"

# Tests
git commit -m "test: add unit tests for auth service"
```

### Making a Pull Request
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: describe your feature"

# Push branch
git push origin feature/your-feature

# Create PR on GitHub
# Fill out PR template
# Request reviewers
# Address feedback
# Merge when approved
```

---

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://admin:password@localhost/claude_remote
JWT_SECRET=dev-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=true
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost
CLAUDE_CODE_PATH=claude
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Development Best Practices

### Backend
- Use type hints (Python 3.12+ syntax)
- Write async code for I/O operations
- Use proper error handling with FastAPI exceptions
- Add docstrings to functions
- Run mypy before committing
- Keep services focused and testable

### Frontend
- Use TypeScript strict mode
- Follow Vue 3 Composition API patterns
- Use Pinia stores for state
- Component tests for critical logic
- Use Tailwind for styling consistency
- Keep components focused and reusable

### General
- Write tests for new features (TDD)
- Keep commits atomic and logical
- Use meaningful branch/commit names
- Document non-obvious code
- Review code before merging
- Run linters before committing

---

## Useful Commands Reference

```bash
# Backend
cd backend
python -m venv venv           # Create venv
source venv/bin/activate      # Activate (Linux/Mac)
pip install -r requirements.txt # Install deps
PYTHONPATH=. alembic upgrade head  # Migrate DB
python src/main.py            # Run server
pytest tests/                  # Run tests
ruff check .                   # Lint
ruff format .                  # Format

# Frontend
cd frontend
npm install                    # Install deps
npm run dev                    # Run dev server
npm run build                  # Build for production
npm run test                   # Run tests
npm run lint                   # Lint

# Git
git checkout 001-web-app-remote    # Switch branch
git pull origin                    # Get latest
git branch -a                      # List branches
git status                         # Check status
git diff                           # View changes
git add .                          # Stage all
git commit -m "message"            # Commit
git push origin branch-name        # Push
```

---

## Next Steps

1. **Clone & Setup** - Follow steps above
2. **Read Code** - Explore src/ structure
3. **Run Tests** - Ensure everything works
4. **Make Small Change** - Create a feature branch
5. **Submit PR** - Get feedback
6. **Join Development** - Start contributing!

---

## Getting Help

- **Code Structure**: See `plan.md`
- **Database Schema**: See `data-model.md`
- **API Spec**: See `contracts/rest-api.md`
- **WebSocket Protocol**: See `contracts/websocket-protocol.md`
- **Implementation Status**: See `IMPLEMENTATION_STATUS.md`
- **API Docs**: http://localhost:8000/docs (after running)

---

**Happy coding! 🚀**

Generated: 2025-10-20  
Branch: `001-web-app-remote`

