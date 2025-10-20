# REST API Contract

**Version**: 1.0.0
**Created**: 2025-10-13
**Base URL**: `http://localhost:8000/api/v1`

## Authentication

All endpoints except `/auth/login` and `/auth/register` require JWT authentication.

**Header**:
```
Authorization: Bearer <access_token>
```

**Token Refresh**:
- Access tokens expire after 1 hour
- Refresh tokens expire after 7 days
- Use `/auth/refresh` to obtain new access token

---

## Endpoints

### Authentication

#### POST /auth/register

**Purpose**: Create new user account

**Request**:
```json
{
  "username": "developer",
  "email": "dev@example.com",
  "password": "SecurePass123!"
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "developer",
    "email": "dev@example.com",
    "created_at": "2025-10-13T10:00:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Errors**:
- 400: Validation error (weak password, invalid email)
- 409: Username or email already exists

---

#### POST /auth/login

**Purpose**: Authenticate user and obtain tokens

**Request**:
```json
{
  "username": "developer",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "developer",
    "email": "dev@example.com"
  }
}
```

**Errors**:
- 401: Invalid credentials
- 403: Account inactive

---

#### POST /auth/refresh

**Purpose**: Obtain new access token using refresh token

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Errors**:
- 401: Invalid or expired refresh token

---

#### POST /auth/logout

**Purpose**: Invalidate refresh token (access token expires naturally)

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (204 No Content)

---

### Sessions

#### GET /sessions

**Purpose**: List user's sessions

**Query Parameters**:
- `status` (optional): Filter by status (ACTIVE, ENDED, etc.)
- `limit` (optional, default 50): Max results
- `offset` (optional, default 0): Pagination offset

**Response** (200 OK):
```json
{
  "sessions": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Project debugging session",
      "status": "ACTIVE",
      "created_at": "2025-10-13T10:00:00Z",
      "last_activity": "2025-10-13T10:30:00Z",
      "message_count": 15
    },
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "title": "Feature development",
      "status": "ENDED",
      "created_at": "2025-10-12T14:00:00Z",
      "last_activity": "2025-10-12T18:30:00Z",
      "ended_at": "2025-10-12T18:30:00Z",
      "message_count": 42
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

---

#### POST /sessions

**Purpose**: Create new session

**Request**:
```json
{
  "title": "New debugging session",
  "working_directory": "/home/user/project"
}
```

**Response** (201 Created):
```json
{
  "id": "323e4567-e89b-12d3-a456-426614174002",
  "title": "New debugging session",
  "status": "CREATED",
  "created_at": "2025-10-13T11:00:00Z",
  "last_activity": "2025-10-13T11:00:00Z",
  "working_directory": "/home/user/project",
  "websocket_url": "ws://localhost:8000/ws/323e4567-e89b-12d3-a456-426614174002"
}
```

**Errors**:
- 400: Invalid working directory

---

#### GET /sessions/{session_id}

**Purpose**: Get session details

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Project debugging session",
  "status": "ACTIVE",
  "created_at": "2025-10-13T10:00:00Z",
  "last_activity": "2025-10-13T10:30:00Z",
  "working_directory": "/home/user/project",
  "claude_process": {
    "status": "RUNNING",
    "pid": 12345,
    "started_at": "2025-10-13T10:00:05Z",
    "restart_count": 0
  },
  "message_count": 15,
  "websocket_url": "ws://localhost:8000/ws/123e4567-e89b-12d3-a456-426614174000"
}
```

**Errors**:
- 404: Session not found
- 403: Session belongs to different user

---

#### PATCH /sessions/{session_id}

**Purpose**: Update session metadata

**Request**:
```json
{
  "title": "Updated session title"
}
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Updated session title",
  "status": "ACTIVE",
  "created_at": "2025-10-13T10:00:00Z",
  "last_activity": "2025-10-13T10:30:00Z"
}
```

**Errors**:
- 404: Session not found
- 403: Session belongs to different user

---

#### DELETE /sessions/{session_id}

**Purpose**: End session and terminate Claude Code process

**Response** (204 No Content)

**Errors**:
- 404: Session not found
- 403: Session belongs to different user

**Side Effects**:
- Terminates Claude Code subprocess
- Sets session status to ENDED
- Closes active WebSocket connections

---

### Messages

#### GET /sessions/{session_id}/messages

**Purpose**: Retrieve conversation history

**Query Parameters**:
- `limit` (optional, default 50): Max messages
- `offset` (optional, default 0): Pagination offset
- `before` (optional): Get messages before this timestamp
- `after` (optional): Get messages after this timestamp

**Response** (200 OK):
```json
{
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "role": "user",
      "content": "list files in current directory",
      "content_type": "text",
      "timestamp": "2025-10-13T10:30:00Z",
      "sequence_number": 1
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "role": "assistant",
      "content": "Files in current directory:\n1. app.py\n2. config.json",
      "content_type": "text",
      "timestamp": "2025-10-13T10:30:02Z",
      "sequence_number": 2,
      "metadata": {
        "execution_time_ms": 1800
      }
    }
  ],
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

**Errors**:
- 404: Session not found
- 403: Session belongs to different user

---

#### DELETE /sessions/{session_id}/messages

**Purpose**: Clear conversation history for session

**Response** (204 No Content)

**Errors**:
- 404: Session not found
- 403: Session belongs to different user

**Side Effects**:
- Deletes all messages for session
- Does not affect session status or Claude process

---

### Process Management

#### POST /sessions/{session_id}/process/start

**Purpose**: Start Claude Code process for session

**Request**:
```json
{
  "working_directory": "/home/user/project"
}
```

**Response** (200 OK):
```json
{
  "process_id": 12345,
  "status": "STARTING",
  "started_at": "2025-10-13T11:00:00Z",
  "working_directory": "/home/user/project"
}
```

**Errors**:
- 409: Process already running for this session
- 500: Failed to start process

---

#### POST /sessions/{session_id}/process/restart

**Purpose**: Restart Claude Code process

**Response** (200 OK):
```json
{
  "process_id": 12346,
  "status": "STARTING",
  "started_at": "2025-10-13T11:05:00Z",
  "restart_count": 1
}
```

**Errors**:
- 429: Too many restart attempts (max 3 per session)
- 500: Failed to restart process

---

#### POST /sessions/{session_id}/process/stop

**Purpose**: Stop Claude Code process gracefully

**Response** (204 No Content)

**Side Effects**:
- Sends SIGTERM to Claude process
- Updates session status to DISCONNECTED
- Process state marked as STOPPED

---

### Health Check

#### GET /health

**Purpose**: Check API health status

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-13T11:00:00Z",
  "services": {
    "database": "connected",
    "websocket": "available"
  }
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "timestamp": "2025-10-13T11:00:00Z",
    "request_id": "770e8400-e29b-41d4-a716-446655440002"
  }
}
```

**Common Error Codes**:
- `VALIDATION_ERROR`: Request validation failed
- `AUTHENTICATION_ERROR`: Invalid or expired token
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource does not exist
- `CONFLICT`: Resource conflict (e.g., duplicate username)
- `RATE_LIMIT`: Too many requests
- `INTERNAL_ERROR`: Server error

---

## Rate Limiting

**Global Limits**:
- 100 requests per minute per user across all endpoints
- 429 response when exceeded with `Retry-After` header

**Endpoint-Specific Limits**:
- POST /auth/login: 5 attempts per 5 minutes per IP
- POST /auth/register: 3 attempts per hour per IP
- POST /sessions: 10 new sessions per hour per user

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1697203200
```

---

## CORS

**Allowed Origins**: Configure via environment variable
- Development: `http://localhost:5173`
- Production: Specific domain

**Allowed Methods**: `GET, POST, PATCH, DELETE, OPTIONS`

**Allowed Headers**: `Authorization, Content-Type`

---

## Pagination

Endpoints returning lists support pagination:

**Query Parameters**:
- `limit`: Max items per page (default 50, max 100)
- `offset`: Skip N items (default 0)

**Response Metadata**:
```json
{
  "data": [...],
  "total": 150,
  "limit": 50,
  "offset": 0,
  "next": "/api/v1/sessions?limit=50&offset=50",
  "previous": null
}
```

---

## Testing Contract Compliance

### Backend Tests (pytest)
```python
async def test_create_session(client: TestClient, auth_headers):
    response = await client.post(
        "/api/v1/sessions",
        json={"title": "Test session", "working_directory": "/tmp"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "CREATED"
```

### Frontend Tests (Vitest)
```typescript
test('creates session via API', async () => {
  const api = new ApiClient('http://localhost:8000', mockToken)
  const session = await api.createSession({
    title: 'Test session',
    working_directory: '/tmp'
  })
  expect(session.id).toBeDefined()
  expect(session.status).toBe('CREATED')
})
```

---

## OpenAPI Specification

Full OpenAPI 3.0 spec available at: `/api/v1/openapi.json`

Interactive docs (Swagger UI): `/docs`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-13 | Initial API specification |

---

## Summary

**Total Endpoints**: 15
**Authentication**: JWT Bearer token
**Rate Limiting**: 100 req/min global, endpoint-specific limits
**Pagination**: Offset-based with limit/offset parameters
**Error Format**: Consistent JSON structure with error codes

**Next**: Create quickstart guide for developers.
