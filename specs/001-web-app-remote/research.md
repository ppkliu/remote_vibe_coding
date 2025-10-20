# Research: Claude Code Remote Web Controller

**Created**: 2025-10-13
**Purpose**: Resolve technical unknowns and establish best practices for implementation

## R1: Claude Code Process Communication Strategy

**Decision**: Use subprocess with stdin/stdout pipes for bidirectional communication

**Rationale**:
- Claude Code console mode operates as a standard CLI tool accepting commands via stdin
- Python's `asyncio.subprocess` provides non-blocking I/O suitable for FastAPI async context
- Stdout/stderr separation allows distinguishing normal output from errors
- No need for modification to Claude Code itself - works with existing binary

**Alternatives Considered**:
- **PTY (pseudo-terminal)**: More complex, handles ANSI codes better but adds unnecessary complexity for MVP
- **Named pipes/FIFOs**: Platform-specific, more complex setup than direct pipes
- **Claude Code API**: Not available for console mode, would require Claude Code modifications

**Implementation Notes**:
- Use `asyncio.create_subprocess_exec()` with `stdin=PIPE`, `stdout=PIPE`, `stderr=PIPE`
- Read output in non-blocking async loops using `StreamReader.readline()`
- Handle process lifecycle: startup, health checks, graceful shutdown
- Buffer management: Use asyncio queues to handle backpressure

---

## R2: Real-time Communication: WebSocket vs SSE

**Decision**: Use WebSocket for bidirectional command/response, with SSE as fallback option

**Rationale**:
- WebSocket provides full-duplex communication needed for sending commands and receiving streaming responses
- Lower latency than HTTP polling or SSE alone
- Better suited for interactive command-response patterns
- FastAPI has excellent WebSocket support via Starlette
- Browser support is universal in modern browsers

**Alternatives Considered**:
- **SSE only**: Only supports server-to-client streaming, would require separate HTTP POST for commands
- **Long polling**: Higher latency and overhead than WebSocket
- **gRPC-web**: Overkill for this use case, requires additional infrastructure

**Implementation Notes**:
- Use FastAPI `WebSocket` endpoint at `/ws/{session_id}`
- Implement heartbeat/ping-pong to detect disconnections (30-second interval)
- Graceful reconnection: Client retries with exponential backoff (1s, 2s, 4s, 8s, max 30s)
- Message protocol: JSON-encoded messages with `type`, `payload`, `timestamp` fields
- Handle connection state in backend: track active WebSocket connections per session

---

## R3: Session Persistence and State Management

**Decision**: PostgreSQL with SQLAlchemy async for session and conversation storage

**Rationale**:
- Relational model fits session metadata structure (users, sessions, messages)
- ACID guarantees ensure session consistency across crashes
- SQLAlchemy async (with asyncpg driver) integrates cleanly with FastAPI async runtime
- PostgreSQL JSON fields support flexible message payload storage
- Mature tooling and deployment experience

**Alternatives Considered**:
- **Redis**: Fast but requires separate persistence configuration, less structured data model
- **SQLite**: Simpler but lacks concurrent write performance for multi-user scenarios
- **In-memory only**: Loses sessions on server restart, violates 24-hour persistence requirement

**Implementation Notes**:
- Use SQLAlchemy 2.0+ async API with `AsyncSession`
- Connection pooling: `create_async_engine` with pool size 10-20
- Schema:
  ```sql
  users (id, username, hashed_password, created_at)
  sessions (id, user_id, claude_process_pid, created_at, last_activity, status)
  messages (id, session_id, role [user/assistant], content, timestamp)
  ```
- Index on `sessions.last_activity` for efficient session cleanup queries
- Automatic session cleanup: Cron job or background task removes sessions idle >24 hours

---

## R4: Authentication Strategy for MVP

**Decision**: Simple session-based authentication with JWT tokens, bcrypt for password hashing

**Rationale**:
- JWT tokens enable stateless authentication scalable across multiple backend instances
- Short-lived access tokens (1 hour) with refresh tokens (7 days) balance security and UX
- bcrypt is industry standard for password hashing with built-in salt
- Simple enough for MVP, extensible to OAuth2/SSO later

**Alternatives Considered**:
- **No authentication**: Insecure, violates FR-013 requirement
- **Basic auth**: Simpler but sends credentials with every request
- **OAuth2 only**: Over-engineered for MVP, can add later

**Implementation Notes**:
- Use `python-jose` for JWT generation/validation
- Use `passlib[bcrypt]` for password hashing
- Store hashed passwords in `users` table
- Login flow: POST /auth/login returns access + refresh tokens
- Protected endpoints verify JWT using FastAPI dependency injection
- Frontend stores JWT in httpOnly cookie or localStorage (with XSS considerations)

---

## R5: Frontend State Management Approach

**Decision**: Vue 3 Composition API with Pinia for global state

**Rationale**:
- Composition API is Vue 3 standard, provides better TypeScript support than Options API
- Pinia is official Vue state management (successor to Vuex), lightweight and intuitive
- Pinia stores for: auth state, active session, WebSocket connection, message history
- Composables for reusable logic: `useWebSocket`, `useSession`, `useAuth`
- No over-engineering: Pinia sufficient for this scale, no need for complex patterns

**Alternatives Considered**:
- **Vuex**: Older, more boilerplate than Pinia
- **No state management**: Prop drilling becomes unwieldy with nested components
- **Redux/Zustand**: React-focused, not idiomatic for Vue

**Implementation Notes**:
- Pinia stores:
  - `useAuthStore`: User authentication state, login/logout actions
  - `useSessionStore`: Active session data, session list
  - `useMessagesStore`: Conversation history, add message actions
  - `useConnectionStore`: WebSocket connection status, reconnection logic
- Composables wrap store access and provide reactive refs
- Persist auth state to localStorage using `pinia-plugin-persistedstate`

---

## R6: Vue Shadcn UI Integration

**Decision**: Use `shadcn-vue` component library with Radix Vue primitives

**Rationale**:
- Shadcn-vue provides accessible, customizable components built on Radix Vue
- TailwindCSS-based styling integrates seamlessly with project requirements
- Copy-paste components model (not npm package) gives full control and customization
- Includes essential components: Button, Input, Card, Dialog, ScrollArea
- Accessibility built-in (ARIA attributes, keyboard navigation)

**Implementation Notes**:
- Initialize with: `npx shadcn-vue@latest init`
- Add components as needed: Button, Input, Card, ScrollArea, Dialog, Alert
- Key components for this app:
  - `CommandInput`: Use Input + Button for command submission
  - `OutputDisplay`: Use ScrollArea + Card for message display
  - `ConnectionStatus`: Use Badge component for connection indicator
  - `SessionList`: Use Card + ScrollArea for session management
- Customize theme via `tailwind.config.js` (colors, typography, spacing)

---

## R7: Real-time Output Streaming Implementation

**Decision**: Server-side async generator streaming through WebSocket

**Rationale**:
- FastAPI WebSocket can send messages as Claude Code produces output (chunk-by-chunk)
- Python async generators allow yielding output incrementally from subprocess
- Frontend receives WebSocket messages and appends to UI in real-time
- Meets <500ms latency requirement per chunk

**Implementation Pattern**:
```python
async def stream_claude_output(process, websocket):
    async for line in process.stdout:
        await websocket.send_json({
            "type": "output_chunk",
            "content": line.decode(),
            "timestamp": datetime.utcnow().isoformat()
        })
```

**Frontend Handling**:
- WebSocket `onmessage` handler appends chunks to reactive message array
- Vue reactivity automatically updates UI
- Auto-scroll to bottom unless user has scrolled up manually (check scroll position)

---

## R8: Error Handling and Recovery Patterns

**Decision**: Layered error handling with user-friendly messages and automatic retry

**Rationale**:
- Claude Code process errors: Capture stderr, display in UI, allow restart
- Network errors: Automatic reconnection with exponential backoff
- Authentication errors: Clear token, redirect to login
- Validation errors: Show inline errors on form fields

**Error Categories**:
1. **Process Errors**: Claude Code crashes, invalid commands
   - Display stderr output to user
   - Offer "Restart Claude Code" button
   - Log full error server-side for debugging

2. **Connection Errors**: WebSocket disconnect, network timeout
   - Show "Reconnecting..." status indicator
   - Automatic retry with backpressure: 1s, 2s, 4s, 8s, 30s (max)
   - After 5 failures, prompt user to refresh page

3. **Authentication Errors**: Invalid token, expired session
   - Clear stored credentials
   - Redirect to login page
   - Preserve session ID in URL to resume after re-auth

4. **Validation Errors**: Empty commands, rate limit exceeded
   - Inline error messages below input field
   - Disable submit button during rate limit cooldown
   - Client-side validation before server submission

---

## R9: Development and Testing Strategy

**Decision**: Parallel development with mocked interfaces, contract-first approach

**Rationale**:
- Frontend and backend can develop simultaneously using agreed-upon contracts
- Mock WebSocket responses for frontend development
- Contract tests ensure both sides adhere to message format
- Vitest for fast unit tests, Playwright for E2E user flows

**Development Workflow**:
1. Define message contracts first (JSON schemas in `/contracts/`)
2. Backend implements contracts with pytest tests
3. Frontend implements against contracts with Vitest tests
4. Integration tests verify end-to-end flow
5. E2E tests validate user stories from spec

**Testing Layers**:
- **Backend Unit**: Test individual services (session manager, auth) with pytest
- **Backend Integration**: Test API endpoints with TestClient (FastAPI)
- **Backend Contract**: Test WebSocket message formats match spec
- **Frontend Unit**: Test components and composables with Vitest
- **Frontend Integration**: Test component interactions with Vitest
- **E2E**: Test complete user flows with Playwright (P1 story first)

---

## R10: Deployment and Infrastructure

**Decision**: Docker Compose for local development, containerized deployment

**Rationale**:
- Docker Compose orchestrates PostgreSQL, backend, frontend for easy setup
- Consistent environment across development machines
- Production deployment can use same containers with orchestration (Docker Swarm, K8s)
- `uv` in backend container for fast Python dependency installation

**docker-compose.yml Structure**:
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: claude_remote
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: <from env>
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://admin:pass@postgres/claude_remote
      JWT_SECRET: <from env>
    depends_on:
      - postgres
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    environment:
      VITE_API_URL: http://localhost:8000
    ports:
      - "5173:5173"
    depends_on:
      - backend

volumes:
  postgres_data:
```

**Environment Variables**:
- Backend: `DATABASE_URL`, `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- Frontend: `VITE_API_URL`, `VITE_WS_URL`
- Use `.env` file locally, environment injection in production

---

## Summary

All technical unknowns resolved. Key architectural decisions:
1. Subprocess communication with async pipes
2. WebSocket for bidirectional real-time communication
3. PostgreSQL + SQLAlchemy async for persistence
4. JWT-based authentication
5. Vue 3 Composition API + Pinia for frontend state
6. Shadcn-vue for UI components
7. Docker Compose for infrastructure

**Next Phase**: Design data models, API contracts, and quickstart guide.
