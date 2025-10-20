# Data Model: Claude Code Remote Web Controller

**Created**: 2025-10-13
**Purpose**: Define data entities, relationships, and state management

## Entity Relationship Diagram

```
User (1) ────── (M) Session (1) ────── (M) Message
                            │
                            └── (1) ClaudeProcess
```

---

## Entity: User

**Purpose**: Represents an authenticated developer who can control Claude Code instances

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique user identifier |
| username | String(50) | UNIQUE, NOT NULL | User login name |
| email | String(255) | UNIQUE, NOT NULL | User email address |
| hashed_password | String(255) | NOT NULL | bcrypt hashed password |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| last_login | DateTime | NULL | Last successful login timestamp |
| is_active | Boolean | NOT NULL, DEFAULT TRUE | Account active status |

### Validation Rules
- Username: 3-50 characters, alphanumeric + underscore/hyphen
- Email: Valid email format (RFC 5322)
- Password (pre-hash): Minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 number
- hashed_password: bcrypt hash with salt rounds = 12

### State Transitions
- **Created** → **Active** (default on registration)
- **Active** → **Inactive** (admin deactivation or user request)
- **Inactive** → **Active** (reactivation by admin)

---

## Entity: Session

**Purpose**: Represents an active connection between a web client and a Claude Code instance

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique session identifier |
| user_id | UUID | FK → User.id, NOT NULL | Owner of this session |
| title | String(255) | NULL | User-defined session name |
| claude_process_pid | Integer | NULL | OS process ID of Claude Code instance |
| status | Enum | NOT NULL | Session status (see below) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Session start timestamp |
| last_activity | DateTime | NOT NULL, DEFAULT NOW() | Last command/message timestamp |
| ended_at | DateTime | NULL | Session termination timestamp |
| connection_id | String(100) | NULL | Active WebSocket connection ID |

### Status Enum Values
- `CREATED`: Session initialized but no Claude Code process started
- `CONNECTING`: Attempting to start Claude Code process
- `ACTIVE`: Claude Code running and connected
- `DISCONNECTED`: WebSocket disconnected but Claude process still running
- `RECONNECTING`: Attempting to restore connection
- `IDLE`: No activity for >5 minutes, Claude process may be suspended
- `ENDED`: Session terminated, Claude process stopped

### Validation Rules
- title: Optional, max 255 characters
- last_activity: Must be updated on every command or message
- claude_process_pid: Must be valid OS PID when status is ACTIVE

### State Transitions
```
CREATED → CONNECTING → ACTIVE ⇄ DISCONNECTED → RECONNECTING → ACTIVE
                  ↓                   ↓
                ENDED               ENDED
                  ↓                   ↓
              (IDLE timeout)   (manual close)
```

### Relationships
- **User** (1:M): One user can have multiple sessions
- **Message** (1:M): One session contains multiple messages
- **ClaudeProcess** (1:1): One session maps to one Claude Code process

---

## Entity: Message

**Purpose**: Represents a single command or response in the conversation history

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique message identifier |
| session_id | UUID | FK → Session.id, NOT NULL | Parent session |
| role | Enum | NOT NULL | Message sender (user/assistant/system) |
| content | Text | NOT NULL | Message text content |
| content_type | Enum | NOT NULL, DEFAULT 'text' | Content format (text/code/error/json) |
| metadata | JSONB | NULL | Additional structured data |
| timestamp | DateTime | NOT NULL, DEFAULT NOW() | Message creation time |
| sequence_number | Integer | NOT NULL | Order within session (1, 2, 3...) |
| is_streamed | Boolean | NOT NULL, DEFAULT FALSE | True if sent in chunks |
| parent_message_id | UUID | FK → Message.id, NULL | For threaded conversations (future) |

### Role Enum Values
- `user`: Command sent by user
- `assistant`: Response from Claude Code
- `system`: System-generated message (errors, status updates)

### Content Type Enum Values
- `text`: Plain text message
- `code`: Code block with syntax highlighting info in metadata
- `error`: Error message from Claude Code or system
- `json`: Structured data (tool use, file operations)
- `markdown`: Formatted markdown content

### Metadata Schema (JSONB)
```json
{
  "language": "python",           // For code content_type
  "file_path": "/path/to/file",   // For file operations
  "tool_name": "ReadFile",        // For tool use messages
  "error_code": "ERR_PROCESS",    // For error messages
  "chunks_count": 5,              // For streamed messages
  "execution_time_ms": 1234       // Command execution duration
}
```

### Validation Rules
- content: NOT empty, max 100KB per message
- sequence_number: Must be sequential within session, starts at 1
- metadata: Must be valid JSON if present

### Relationships
- **Session** (M:1): Multiple messages belong to one session
- **ParentMessage** (self-referential): Supports message threading (future)

---

## Entity: ClaudeProcess

**Purpose**: Represents runtime state of a Claude Code subprocess

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | Unique process record ID |
| session_id | UUID | FK → Session.id, UNIQUE, NOT NULL | Associated session |
| process_id | Integer | NOT NULL | OS process ID (PID) |
| started_at | DateTime | NOT NULL, DEFAULT NOW() | Process start time |
| last_heartbeat | DateTime | NOT NULL | Last health check timestamp |
| status | Enum | NOT NULL | Process health status |
| working_directory | String(500) | NOT NULL | Claude Code working directory |
| environment_vars | JSONB | NULL | Environment variables passed to process |
| restart_count | Integer | NOT NULL, DEFAULT 0 | Number of restarts in this session |

### Status Enum Values
- `STARTING`: Process launching
- `RUNNING`: Process active and healthy
- `UNHEALTHY`: Heartbeat missed, may be unresponsive
- `CRASHED`: Process exited unexpectedly
- `STOPPED`: Process terminated gracefully

### Validation Rules
- process_id: Must be valid and running PID
- last_heartbeat: Updated every 30 seconds, alert if >60s stale
- working_directory: Must be absolute path, exist on filesystem
- restart_count: Max 3 restarts per session, then mark session as ENDED

### State Transitions
```
STARTING → RUNNING ⇄ UNHEALTHY → CRASHED → (restart) → STARTING
             ↓            ↓                                ↓
           STOPPED      STOPPED                         STOPPED
```

### Relationships
- **Session** (1:1): One Claude process per session

---

## Indexes

**Performance Optimizations**

```sql
-- Session queries
CREATE INDEX idx_session_user_id ON sessions(user_id);
CREATE INDEX idx_session_status ON sessions(status);
CREATE INDEX idx_session_last_activity ON sessions(last_activity);

-- Message queries
CREATE INDEX idx_message_session_id ON messages(session_id);
CREATE INDEX idx_message_session_sequence ON messages(session_id, sequence_number);
CREATE INDEX idx_message_timestamp ON messages(timestamp);

-- Process monitoring
CREATE INDEX idx_claude_process_status ON claude_processes(status);
CREATE INDEX idx_claude_process_last_heartbeat ON claude_processes(last_heartbeat);

-- User lookups
CREATE UNIQUE INDEX idx_user_username ON users(username);
CREATE UNIQUE INDEX idx_user_email ON users(email);
```

---

## Data Retention and Cleanup

### Automatic Cleanup Rules

1. **Idle Sessions**: Sessions with `last_activity` > 24 hours ago
   - Mark as `ENDED`
   - Terminate associated Claude process
   - Retain messages for 7 days before archival

2. **Old Messages**: Messages from sessions ended > 7 days ago
   - Move to archive table (not implemented in MVP)
   - Or hard delete if user confirms

3. **Inactive Users**: Users with no login > 90 days
   - Mark as `is_active = FALSE`
   - Email notification before deactivation
   - Do not delete sessions (for data recovery)

4. **Failed Processes**: Claude processes in `CRASHED` status > 1 hour
   - Clean up process record
   - Update session status to `ENDED`

### Manual Cleanup Actions

- User can delete individual sessions (soft delete: set ended_at)
- User can delete message history (hard delete messages)
- Admin can purge inactive users after notification period

---

## Validation Summary

| Entity | Primary Validations |
|--------|---------------------|
| User | Email format, password strength, unique username/email |
| Session | Valid status transitions, PID validity, activity timeout |
| Message | Non-empty content, valid JSON metadata, sequential ordering |
| ClaudeProcess | Running PID, heartbeat freshness, restart limits |

---

## State Management (Frontend)

### Pinia Store Structure

```typescript
// stores/auth.ts
interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}

// stores/session.ts
interface SessionState {
  activeSession: Session | null
  sessions: Session[]
  isLoading: boolean
  error: string | null
}

// stores/messages.ts
interface MessagesState {
  messages: Message[]
  isStreaming: boolean
  currentMessageId: string | null
}

// stores/connection.ts
interface ConnectionState {
  status: 'disconnected' | 'connecting' | 'connected' | 'reconnecting'
  websocket: WebSocket | null
  reconnectAttempts: number
  lastError: string | null
}
```

### Reactive Data Flow

1. User sends command → `messagesStore.sendMessage()`
2. Store dispatches via WebSocket → Backend receives
3. Backend streams response → WebSocket `onmessage`
4. Store appends message chunks → Vue reactivity updates UI
5. Message complete → Store marks streaming as false

---

## Summary

**Total Entities**: 4 (User, Session, Message, ClaudeProcess)
**Total Relationships**: 4 (User-Session, Session-Message, Session-ClaudeProcess, Message-ParentMessage)
**Key Validations**: Email format, password strength, PID validity, heartbeat monitoring
**Retention Policy**: 24-hour session timeout, 7-day message retention

**Next**: Define API contracts for WebSocket and REST endpoints.
