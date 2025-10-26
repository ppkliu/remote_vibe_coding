# Claude Code Remote Web Controller

A web application that enables remote control of Claude Code running in console mode through a browser interface.

## Features

- 🎯 **Remote Command Execution**: Send commands to Claude Code from web browser
- 📡 **Real-time Output Streaming**: See Claude Code responses progressively as generated
- 💾 **Session Management**: Maintain sessions across disconnections and browser restarts
- 🔒 **Secure Authentication**: JWT-based authentication with user accounts
- 🔄 **Auto-Reconnection**: Automatic reconnection with exponential backoff
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Database for session and message storage
- **SQLAlchemy** - ORM with async support
- **WebSocket** - Real-time bidirectional communication

### Frontend
- **Vue 3** - Progressive JavaScript framework  
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework

## Quick Start with Docker

### 1. Start all services

\`\`\`bash
docker-compose up --build
\`\`\`

This starts:
- PostgreSQL on \`localhost:5432\`
- Backend API on \`http://localhost:8000\`
- Frontend on \`http://localhost:5173\`

### 2. Access the application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

### 3. Create account and start

1. Register at http://localhost:5173/register
2. Login with your credentials
3. Click "New Session"
4. Send commands and see real-time responses!

## Manual Setup

### Backend

\`\`\`bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install uv
uv pip install -e ".[dev]"

cp .env.example .env
# Edit .env with database credentials

alembic upgrade head
uvicorn src.main:app --reload
\`\`\`

### Frontend

\`\`\`bash
cd frontend
npm install
cp .env.example .env
npm run dev
\`\`\`

## Configuration

See \`.env.example\` files in backend/ and frontend/ directories.

Key variables:
- \`DATABASE_URL\`: PostgreSQL connection string
- \`JWT_SECRET\`: Secret key for JWT tokens (change in production!)
- \`CLAUDE_CODE_PATH\`: Path to claude executable

## Logging & Debugging

The application includes comprehensive logging for WebSocket connections and Claude Code communication.

### Quick Overview

**Default Behavior** (out of the box):
- ✅ Console: Clean application logs (no SQL)
- ✅ File: Complete history with DEBUG details
- ✅ Log rotation: 3MB × 3 files = 9MB total
- ✅ Emoji indicators for quick scanning (✅ ❌ 📨 📦 🔨 🔌)

### Configuration

\`\`\`bash
# In backend/.env
LOG_DIR=logs
LOG_LEVEL=INFO
SQLALCHEMY_LOG_LEVEL=WARNING  # Hide SQL by default
\`\`\`

**To enable SQL logging** (for debugging):
\`\`\`bash
# Change in .env
SQLALCHEMY_LOG_LEVEL=INFO

# Restart backend
python3.12 -m uvicorn src.main:app --reload
\`\`\`

### Log Files

\`\`\`
backend/logs/
├── app.log         # Current log (up to 3MB)
├── app.log.1       # Backup 1 (3MB)
├── app.log.2       # Backup 2 (3MB)
└── app.log.3       # Backup 3 (3MB)
\`\`\`

**View logs**:
\`\`\`bash
# Live tail
tail -f backend/logs/app.log

# Recent errors
tail -50 backend/logs/app.log | grep -i error

# Filter by session
grep "Session: abc-123" backend/logs/app.log
\`\`\`

### Documentation

Comprehensive logging documentation available:

- **[LOGGING_GUIDE.md](./LOGGING_GUIDE.md)** - Operator guide for configuration and troubleshooting
- **[LOGGING_REFERENCE.md](./LOGGING_REFERENCE.md)** - Complete catalog of all 60+ logging points
- **[tests/TESTING_QUICKSTART.md](./tests/TESTING_QUICKSTART.md)** - Developer guide for running logging tests
- **[tests/integration/MESSAGE_FLOW_GUIDE.md](./tests/integration/MESSAGE_FLOW_GUIDE.md)** - Message flow tracing guide
- **[CLAUDE_PROCESS_LIFECYCLE.md](./CLAUDE_PROCESS_LIFECYCLE.md)** - Process lifecycle debugging

### Example Console Output

\`\`\`
2025-10-23 14:32:10 - src.api.websocket - INFO - ✅ WebSocket connection accepted - Session: abc123, User: user456
2025-10-23 14:32:13 - src.services.claude_bridge - INFO - ✅ Claude Code process started successfully - PID: 12345
2025-10-23 14:32:15 - src.api.websocket - INFO - 🔨 Command received - Session: abc123
2025-10-23 14:32:16 - src.api.websocket - INFO - ✅ Command sent to Claude - Session: abc123
2025-10-23 14:32:18 - src.api.websocket - INFO - ✅ Command execution complete - Session: abc123, Chunks: 5, Time: 2345ms
\`\`\`

### Troubleshooting with Logs

**Problem**: User sends message but gets no response

**Debug steps**:
1. Check logs for session ID: \`grep "Session: <id>" logs/app.log\`
2. Look for error indicators: \`grep "❌" logs/app.log\`
3. Verify Claude process started: \`grep "PID" logs/app.log\`
4. Check command was sent: \`grep "🔨" logs/app.log\`
5. See [LOGGING_GUIDE.md](./LOGGING_GUIDE.md) for detailed troubleshooting

### Testing Logging Features

\`\`\`bash
# Run all logging tests (60+ tests)
cd backend
PYTHONPATH=. python3.12 -m pytest tests/unit/test_logging_level_toggle.py tests/unit/test_sqlalchemy_echo.py tests/integration/test_console_output.py tests/integration/test_websocket_lifecycle.py tests/integration/test_e2e_claude_communication.py -v

# See tests/TESTING_QUICKSTART.md for detailed testing guide
\`\`\`

## Architecture

\`\`\`
Browser (Vue) ◄──WebSocket──► FastAPI ◄──subprocess──► Claude Code
                                   │
                                   ▼
                              PostgreSQL
\`\`\`

## Troubleshooting

**Database issues**: Ensure PostgreSQL is running
**WebSocket fails**: Check CORS settings and firewall
**Claude won't start**: Verify CLAUDE_CODE_PATH

## License

MIT License
