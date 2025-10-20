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
