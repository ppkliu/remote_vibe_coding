# WebSocket Protocol Contract

**Version**: 1.0.0
**Created**: 2025-10-13
**Purpose**: Define WebSocket message format for real-time Claude Code communication

## Connection

### Endpoint
```
WS /ws/{session_id}
```

### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| token | string | Yes | JWT access token for authentication |

### Connection Flow
1. Client initiates WebSocket connection with session_id and token
2. Server validates token and session ownership
3. Server sends `connection_established` message
4. Heartbeat/ping-pong begins (every 30 seconds)
5. Client can send commands, server streams responses

### Authentication
- Token passed as query parameter: `ws://localhost:8000/ws/{session_id}?token={jwt_token}`
- Server validates JWT before upgrading connection
- Connection rejected with 401 if token invalid or expired

---

## Message Format

All messages are JSON objects with the following base structure:

```typescript
interface BaseMessage {
  type: MessageType
  timestamp: string  // ISO 8601 format
  message_id: string // UUID
}
```

---

## Client → Server Messages

### 1. Send Command

**Purpose**: Execute a command in Claude Code

```json
{
  "type": "command",
  "timestamp": "2025-10-13T10:30:00Z",
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "payload": {
    "command": "list files in current directory",
    "session_id": "123e4567-e89b-12d3-a456-426614174000"
  }
}
```

**Payload Schema**:
```typescript
interface CommandPayload {
  command: string      // User command text
  session_id: string   // UUID of active session
}
```

**Validations**:
- `command`: Non-empty string, max 10,000 characters
- `session_id`: Must match WebSocket connection session_id

---

### 2. Cancel Command

**Purpose**: Interrupt a running command

```json
{
  "type": "cancel_command",
  "timestamp": "2025-10-13T10:30:05Z",
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "payload": {
    "command_message_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Payload Schema**:
```typescript
interface CancelCommandPayload {
  command_message_id: string  // UUID of command to cancel
}
```

---

### 3. Tool Approval Response

**Purpose**: Approve or reject Claude Code tool use request

```json
{
  "type": "tool_approval",
  "timestamp": "2025-10-13T10:30:10Z",
  "message_id": "770e8400-e29b-41d4-a716-446655440002",
  "payload": {
    "tool_request_id": "880e8400-e29b-41d4-a716-446655440003",
    "approved": true,
    "reason": null
  }
}
```

**Payload Schema**:
```typescript
interface ToolApprovalPayload {
  tool_request_id: string  // UUID of tool request
  approved: boolean        // true = approve, false = reject
  reason?: string | null   // Optional rejection reason
}
```

---

### 4. Heartbeat Pong

**Purpose**: Respond to server ping to maintain connection

```json
{
  "type": "pong",
  "timestamp": "2025-10-13T10:30:15Z",
  "message_id": "990e8400-e29b-41d4-a716-446655440004",
  "payload": {}
}
```

---

## Server → Client Messages

### 1. Connection Established

**Purpose**: Confirm WebSocket connection successful

```json
{
  "type": "connection_established",
  "timestamp": "2025-10-13T10:30:00Z",
  "message_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "payload": {
    "session_id": "123e4567-e89b-12d3-a456-426614174000",
    "claude_status": "ACTIVE",
    "message_history_count": 15
  }
}
```

**Payload Schema**:
```typescript
interface ConnectionEstablishedPayload {
  session_id: string
  claude_status: 'ACTIVE' | 'CONNECTING' | 'DISCONNECTED'
  message_history_count: number
}
```

---

### 2. Output Chunk (Streaming)

**Purpose**: Stream Claude Code output in real-time

```json
{
  "type": "output_chunk",
  "timestamp": "2025-10-13T10:30:02.500Z",
  "message_id": "bb0e8400-e29b-41d4-a716-446655440006",
  "payload": {
    "command_message_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "Files in current directory:\n",
    "content_type": "text",
    "is_final": false,
    "sequence": 1
  }
}
```

**Payload Schema**:
```typescript
interface OutputChunkPayload {
  command_message_id: string  // UUID of originating command
  content: string             // Chunk of output text
  content_type: 'text' | 'code' | 'error' | 'json'
  is_final: boolean           // true for last chunk
  sequence: number            // Chunk order (1, 2, 3...)
  metadata?: Record<string, any>  // Optional additional data
}
```

---

### 3. Command Complete

**Purpose**: Signal that command execution finished

```json
{
  "type": "command_complete",
  "timestamp": "2025-10-13T10:30:05.800Z",
  "message_id": "cc0e8400-e29b-41d4-a716-446655440007",
  "payload": {
    "command_message_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "success",
    "execution_time_ms": 5800,
    "output_chunks_count": 12
  }
}
```

**Payload Schema**:
```typescript
interface CommandCompletePayload {
  command_message_id: string
  status: 'success' | 'error' | 'cancelled'
  execution_time_ms: number
  output_chunks_count: number
  error_message?: string  // Present if status = 'error'
}
```

---

### 4. Tool Approval Request

**Purpose**: Ask user to approve Claude Code tool use

```json
{
  "type": "tool_approval_request",
  "timestamp": "2025-10-13T10:30:08Z",
  "message_id": "dd0e8400-e29b-41d4-a716-446655440008",
  "payload": {
    "tool_request_id": "880e8400-e29b-41d4-a716-446655440003",
    "tool_name": "ReadFile",
    "tool_description": "Read file contents",
    "arguments": {
      "file_path": "/home/user/project/config.json"
    },
    "timeout_seconds": 60
  }
}
```

**Payload Schema**:
```typescript
interface ToolApprovalRequestPayload {
  tool_request_id: string
  tool_name: string
  tool_description: string
  arguments: Record<string, any>
  timeout_seconds: number
}
```

---

### 5. Error Message

**Purpose**: Report system or process errors

```json
{
  "type": "error",
  "timestamp": "2025-10-13T10:30:10Z",
  "message_id": "ee0e8400-e29b-41d4-a716-446655440009",
  "payload": {
    "error_code": "PROCESS_CRASHED",
    "error_message": "Claude Code process terminated unexpectedly",
    "details": {
      "exit_code": 1,
      "last_output": "Fatal error: ..."
    },
    "recoverable": false
  }
}
```

**Payload Schema**:
```typescript
interface ErrorPayload {
  error_code: ErrorCode
  error_message: string
  details?: Record<string, any>
  recoverable: boolean
}

type ErrorCode =
  | 'PROCESS_CRASHED'
  | 'PROCESS_TIMEOUT'
  | 'INVALID_COMMAND'
  | 'RATE_LIMIT_EXCEEDED'
  | 'SESSION_EXPIRED'
  | 'PERMISSION_DENIED'
  | 'INTERNAL_ERROR'
```

---

### 6. Status Update

**Purpose**: Notify client of session or process status changes

```json
{
  "type": "status_update",
  "timestamp": "2025-10-13T10:30:12Z",
  "message_id": "ff0e8400-e29b-41d4-a716-446655440010",
  "payload": {
    "session_status": "ACTIVE",
    "claude_status": "RUNNING",
    "connection_quality": "good",
    "last_activity": "2025-10-13T10:30:05Z"
  }
}
```

**Payload Schema**:
```typescript
interface StatusUpdatePayload {
  session_status: SessionStatus
  claude_status: ClaudeProcessStatus
  connection_quality: 'excellent' | 'good' | 'poor' | 'unstable'
  last_activity: string  // ISO 8601 timestamp
}
```

---

### 7. Heartbeat Ping

**Purpose**: Check connection liveness

```json
{
  "type": "ping",
  "timestamp": "2025-10-13T10:30:15Z",
  "message_id": "000e8400-e29b-41d4-a716-446655440011",
  "payload": {}
}
```

**Response Required**: Client must respond with `pong` within 5 seconds

---

## Error Handling

### Connection Errors

**Invalid Token**:
- Server closes WebSocket with code 1008 (Policy Violation)
- Close reason: "Invalid or expired authentication token"

**Session Not Found**:
- Server closes WebSocket with code 1008
- Close reason: "Session does not exist or does not belong to user"

**Rate Limit Exceeded**:
- Server sends `error` message with `RATE_LIMIT_EXCEEDED`
- Client must wait before sending next command
- Connection remains open

### Network Interruptions

**Client Disconnected**:
- Server maintains session state for 60 seconds
- Server attempts to save in-flight command results
- Client can reconnect to same session_id within 60 seconds

**Server Disconnect**:
- Client receives WebSocket close event
- Client initiates reconnection with exponential backoff: 1s, 2s, 4s, 8s, 30s (max)
- After 5 failed attempts, prompt user to refresh page

---

## Message Ordering and Delivery Guarantees

### Ordering
- **Commands**: Processed sequentially in order received
- **Output Chunks**: Guaranteed sequential delivery via `sequence` field
- **Tool Approvals**: Matched to requests via `tool_request_id`

### Delivery
- **At-most-once**: No automatic retries on failure
- **Client responsibility**: Detect missing chunks via sequence gaps
- **Server responsibility**: Mark messages as delivered on send

### Idempotency
- **Commands**: Not idempotent - resending may execute twice
- **Tool Approvals**: Idempotent via `tool_request_id` deduplication
- **Heartbeats**: Idempotent

---

## Rate Limiting

**Commands**:
- Max 10 commands per minute per user
- Enforced at WebSocket handler level
- Exceeded limit triggers `RATE_LIMIT_EXCEEDED` error

**Heartbeats**:
- No rate limit on `pong` responses
- Automatically sent every 30 seconds by server

---

## Security Considerations

1. **Authentication**: JWT token validated on connection and stored for duration
2. **Authorization**: Session ownership verified before command execution
3. **Input Validation**: All command payloads sanitized and length-limited
4. **Process Isolation**: Claude Code runs as subprocess, cannot access other sessions
5. **Error Disclosure**: Error messages do not expose system internals

---

## Testing Contract Compliance

### Backend Tests (pytest)
```python
async def test_command_execution():
    async with websocket_client("/ws/session-id?token=valid-jwt") as ws:
        await ws.send_json({
            "type": "command",
            "timestamp": "2025-10-13T10:30:00Z",
            "message_id": str(uuid.uuid4()),
            "payload": {"command": "test command", "session_id": "session-id"}
        })
        response = await ws.receive_json()
        assert response["type"] in ["output_chunk", "command_complete"]
```

### Frontend Tests (Vitest)
```typescript
test('handles output_chunk message', () => {
  const message = {
    type: 'output_chunk',
    timestamp: '2025-10-13T10:30:00Z',
    message_id: uuid(),
    payload: {
      command_message_id: uuid(),
      content: 'test output',
      content_type: 'text',
      is_final: false,
      sequence: 1
    }
  }
  messagesStore.handleWebSocketMessage(message)
  expect(messagesStore.messages).toContainEqual(expect.objectContaining({
    content: 'test output'
  }))
})
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-13 | Initial protocol definition |

---

## Summary

**Message Types**: 11 total (4 client→server, 7 server→client)
**Authentication**: JWT token via query parameter
**Delivery**: At-most-once, sequential ordering
**Rate Limit**: 10 commands/minute
**Heartbeat**: 30-second interval

**Next**: Define REST API contracts for session management and authentication.
