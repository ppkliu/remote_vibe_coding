# Logging Reference: Complete Logging Points Catalog

**Feature**: 002-claude-code WebSocket/Claude Code Communication Logging  
**Total Logging Points**: 60+ across 3 modules  
**Last Updated**: 2025-10-25

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [WebSocket Module (28 logging points)](#websocket-module)
3. [Claude Bridge Module (17 logging points)](#claude-bridge-module)
4. [Logging Configuration](#logging-configuration)
5. [Context Variables](#context-variables)
6. [Log Levels Guide](#log-levels-guide)
7. [Emoji Indicators](#emoji-indicators)

---

## Quick Reference

| Module | Logging Points | Primary Events |
|--------|---------------|----------------|
| `src.api.websocket` | 28 | Connection lifecycle, message flow, command execution |
| `src.services.claude_bridge` | 17 | Process management, command sending, output reading |
| `src.logging_config` | 15+ | Configuration, SQLAlchemy suppression, file rotation |

**Default Behavior**:
- Console: INFO level (clean, no SQL)
- File: DEBUG level (complete history)
- Rotation: 3MB × 3 files = 9MB total

---

## WebSocket Module

**File**: `backend/src/api/websocket.py`  
**Logger Name**: `src.api.websocket`

### Connection Lifecycle (Lines 25-53)

#### WS-001: Connection Request
```python
# Line 25
logger.info(f"WebSocket connection request - Session: {session_id}")
```
- **Level**: INFO
- **When**: Client initiates WebSocket connection
- **Context**: `session_id`
- **Next**: Authentication verification

#### WS-002: Auth Failed
```python
# Line 30
logger.warning(f"❌ WebSocket auth failed - invalid token for session: {session_id}")
```
- **Level**: WARNING ⚠️
- **Emoji**: ❌ (error)
- **When**: Token verification fails
- **Context**: `session_id`
- **Result**: Connection closed with 1008 code

#### WS-003: Token Verified
```python
# Line 35
logger.debug(f"Token verified - User: {user_id}, Session: {session_id}")
```
- **Level**: DEBUG
- **When**: Token successfully verified
- **Context**: `user_id`, `session_id`
- **Next**: Session ownership verification

#### WS-004: Session Not Found
```python
# Line 43
logger.warning(f"❌ WebSocket session not found - Session: {session_id}, User: {user_id}")
```
- **Level**: WARNING ⚠️
- **Emoji**: ❌ (error)
- **When**: Session doesn't exist or doesn't belong to user
- **Context**: `session_id`, `user_id`
- **Result**: Connection closed

#### WS-005: Connection Accepted ✅
```python
# Line 48
logger.info(f"✅ WebSocket connection accepted - Session: {session_id}, User: {user_id}")
```
- **Level**: INFO ⭐
- **Emoji**: ✅ (success)
- **When**: Connection established successfully
- **Context**: `session_id`, `user_id`
- **Visibility**: Console + File
- **Next**: Connection registration

#### WS-006: Connection Registered
```python
# Line 53
logger.debug(f"Connection registered - Connection ID: {connection_id}")
```
- **Level**: DEBUG
- **When**: Connection ID assigned and stored
- **Context**: `connection_id`
- **Visibility**: File only

### Process Management (Lines 62-81)

#### WS-007: Starting New Process
```python
# Line 62
logger.info(f"No active Claude bridge found, starting new process - Session: {session_id}")
```
- **Level**: INFO
- **When**: No existing Claude process for session
- **Context**: `session_id`
- **Next**: Process startup attempt

#### WS-008: Process Started Successfully ✅
```python
# Line 67
logger.info(f"✅ Claude process started successfully - Session: {session_id}")
```
- **Level**: INFO ⭐
- **Emoji**: ✅ (success)
- **When**: Claude Code subprocess created successfully
- **Context**: `session_id`
- **Visibility**: Console + File

#### WS-009: Bridge Not Found After Start
```python
# Line 70
logger.error(f"❌ Claude process started but bridge not found - Session: {session_id}")
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Process created but not accessible in session manager
- **Context**: `session_id`
- **Action**: Connection closed

#### WS-010: Process Start Failed
```python
# Line 75
logger.error(f"❌ Failed to start Claude process - Session: {session_id}, Error: {str(e)}", exc_info=True)
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Exception during process startup
- **Context**: `session_id`, `error`
- **Extra**: Full stack trace (`exc_info=True`)

#### WS-011: Using Existing Bridge
```python
# Line 80
logger.info(f"Using existing Claude bridge - Session: {session_id}")
```
- **Level**: INFO
- **When**: Reconnecting to existing Claude process
- **Context**: `session_id`

### Message Reception (Lines 99-109)

#### WS-012: Message Received
```python
# Line 99
logger.debug(f"📨 WebSocket message received - Session: {session_id}, Data length: {len(data)}")
```
- **Level**: DEBUG
- **Emoji**: 📨 (message)
- **When**: WebSocket receives data from client
- **Context**: `session_id`, `data_length`
- **Visibility**: File only

#### WS-013: Message Type Identified
```python
# Line 104
logger.debug(f"Message type: {msg_type} - Session: {session_id}")
```
- **Level**: DEBUG
- **When**: JSON parsed, message type extracted
- **Context**: `msg_type` (command/pong/tool_approval), `session_id`
- **Visibility**: File only

#### WS-014: Heartbeat Pong
```python
# Line 108
logger.debug(f"Heartbeat pong received - Session: {session_id}")
```
- **Level**: DEBUG
- **When**: Client responds to ping
- **Context**: `session_id`
- **Purpose**: Connection health verification

### Command Execution (Lines 129-232)

#### WS-015: Command Received 🔨
```python
# Line 129
logger.info(f"🔨 Command received - Session: {session_id}, Command: {command[:100]}{'...' if len(command) > 100 else ''}")
```
- **Level**: INFO ⭐
- **Emoji**: 🔨 (command)
- **When**: User sends command to Claude
- **Context**: `session_id`, `command` (truncated to 100 chars)
- **Visibility**: Console + File
- **Next**: Save to database

#### WS-016: User Message Saved
```python
# Line 147
logger.debug(f"User message saved - Message ID: {user_msg.id}, Sequence: {next_seq}")
```
- **Level**: DEBUG
- **When**: User message persisted to database
- **Context**: `message_id`, `sequence_number`
- **Visibility**: File only

#### WS-017: Sending to Claude
```python
# Line 151
logger.info(f"Sending command to Claude - Session: {session_id}")
```
- **Level**: INFO
- **When**: About to send command to Claude subprocess
- **Context**: `session_id`

#### WS-018: Command Sent Successfully ✅
```python
# Line 154
logger.info(f"✅ Command sent to Claude - Session: {session_id}")
```
- **Level**: INFO ⭐
- **Emoji**: ✅ (success)
- **When**: Command written to Claude stdin successfully
- **Context**: `session_id`
- **Visibility**: Console + File

#### WS-019: Starting Output Read
```python
# Line 164
logger.info(f"Starting to read Claude output - Session: {session_id}")
```
- **Level**: INFO
- **When**: Beginning to read from Claude stdout
- **Context**: `session_id`

#### WS-020: Output Chunk Received 📦
```python
# Line 169
logger.debug(f"📦 Output chunk [{chunk_sequence}] - Length: {len(line)}, Session: {session_id}")
```
- **Level**: DEBUG
- **Emoji**: 📦 (output)
- **When**: Each line of output from Claude
- **Context**: `chunk_sequence`, `line_length`, `session_id`
- **Visibility**: File only
- **Frequency**: Per output line (can be many)

#### WS-021: Tool Approval Detected
```python
# Line 174
logger.info(f"Tool approval request detected - Tool: {approval_request['tool_name']}, Session: {session_id}")
```
- **Level**: INFO
- **When**: Claude requests permission to use tool
- **Context**: `tool_name`, `session_id`
- **Next**: Wait for user approval

#### WS-022: Chunk Limit Reached
```python
# Line 193
logger.warning(f"Output chunk limit reached (100 chunks) - Session: {session_id}")
```
- **Level**: WARNING ⚠️
- **When**: More than 100 output chunks received
- **Context**: `session_id`
- **Purpose**: Prevent infinite loops

#### WS-023: Command Complete ✅
```python
# Line 198
logger.info(f"✅ Command execution complete - Session: {session_id}, Chunks: {chunk_sequence}, Time: {execution_time_ms}ms")
```
- **Level**: INFO ⭐
- **Emoji**: ✅ (success)
- **When**: All output read, command finished
- **Context**: `session_id`, `chunks_count`, `execution_time_ms`
- **Visibility**: Console + File
- **Use**: Performance monitoring

#### WS-024: Assistant Response Saved
```python
# Line 212
logger.debug(f"Assistant response saved - Message ID: {assistant_msg.id}")
```
- **Level**: DEBUG
- **When**: Claude's response persisted to database
- **Context**: `message_id`
- **Visibility**: File only

#### WS-025: Command Execution Failed
```python
# Line 221
logger.error(f"❌ Command execution failed - Session: {session_id}, Error: {str(e)}", exc_info=True)
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Exception during command execution
- **Context**: `session_id`, `error`
- **Extra**: Full stack trace

#### WS-026: No Bridge Available
```python
# Line 227
logger.error(f"❌ No Claude bridge available for command - Session: {session_id}")
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Bridge disappeared during command handling
- **Context**: `session_id`

#### WS-027: Invalid JSON
```python
# Line 234
logger.warning(f"❌ Invalid JSON received - Session: {session_id}")
```
- **Level**: WARNING ⚠️
- **Emoji**: ❌ (error)
- **When**: Message parsing fails
- **Context**: `session_id`

### Disconnection (Lines 238-251)

#### WS-028: WebSocket Disconnected 🔌
```python
# Line 238
logger.info(f"🔌 WebSocket disconnected - Session: {session_id}, Connection: {connection_id}")
```
- **Level**: INFO ⭐
- **Emoji**: 🔌 (disconnect)
- **When**: Client disconnects (normal or abnormal)
- **Context**: `session_id`, `connection_id`
- **Visibility**: Console + File

#### WS-029: Unexpected Error
```python
# Line 241
logger.error(f"❌ Unexpected error in WebSocket handler - Session: {session_id}, Error: {str(e)}", exc_info=True)
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Unhandled exception in WebSocket handler
- **Context**: `session_id`, `error`
- **Extra**: Full stack trace

#### WS-030: Cleanup Started
```python
# Line 244
logger.debug(f"Cleaning up WebSocket resources - Session: {session_id}")
```
- **Level**: DEBUG
- **When**: Finally block executing cleanup
- **Context**: `session_id`

#### WS-031: Cleanup Complete ✅
```python
# Line 251
logger.info(f"✅ WebSocket cleanup complete - Session: {session_id}")
```
- **Level**: INFO ⭐
- **Emoji**: ✅ (success)
- **When**: All resources released
- **Context**: `session_id`
- **Visibility**: Console + File

---

## Claude Bridge Module

**File**: `backend/src/services/claude_bridge.py`  
**Logger Name**: `src.services.claude_bridge`

### Process Startup (Lines 22-55)

#### CB-001: Starting Process
```python
# Line 22
logger.info(f"Starting Claude Code process")
```
- **Level**: INFO
- **When**: Beginning subprocess creation
- **Context**: None

#### CB-002: Claude Executable Path
```python
# Line 23
logger.info(f"Claude executable path: {self.claude_path}")
```
- **Level**: INFO
- **When**: About to start process
- **Context**: `claude_path`
- **Use**: Verify correct executable path

#### CB-003: Working Directory
```python
# Line 24
logger.info(f"Working directory: {working_directory}")
```
- **Level**: INFO
- **When**: Before subprocess creation
- **Context**: `working_directory`
- **Use**: Verify correct working directory

#### CB-004: Executable Not Found
```python
# Line 29
logger.error(f"Claude executable not found at: {self.claude_path}")
```
- **Level**: ERROR 🚨
- **When**: File doesn't exist at claude_path
- **Context**: `claude_path`
- **Result**: FileNotFoundError raised

#### CB-005: Working Directory Missing
```python
# Line 34
logger.error(f"Working directory does not exist: {working_directory}")
```
- **Level**: ERROR 🚨
- **When**: Working directory doesn't exist
- **Context**: `working_directory`
- **Result**: FileNotFoundError raised

#### CB-006: Creating Subprocess
```python
# Line 37
logger.debug(f"Creating subprocess with: {self.claude_path}")
```
- **Level**: DEBUG
- **When**: About to call create_subprocess_exec
- **Context**: `claude_path`

#### CB-007: Process Started ✅
```python
# Line 47
logger.info(f"✅ Claude Code process started successfully - PID: {pid}")
```
- **Level**: INFO ⭐
- **Emoji**: ✅ (success)
- **When**: Subprocess created successfully
- **Context**: `pid`
- **Visibility**: Console + File
- **Use**: Track process lifecycle

#### CB-008: File Not Found
```python
# Line 51
logger.error(f"❌ File not found error: {str(e)}")
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: FileNotFoundError during startup
- **Context**: `error`

#### CB-009: Start Failed
```python
# Line 54
logger.error(f"❌ Failed to start Claude Code process: {str(e)}", exc_info=True)
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Any exception during startup
- **Context**: `error`
- **Extra**: Full stack trace

### Command Sending (Lines 57-70)

#### CB-010: Process Not Started
```python
# Line 60
logger.error("❌ Cannot send command - process not started")
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Attempt to send command without active process
- **Result**: RuntimeError raised

#### CB-011: Sending Command
```python
# Line 64
logger.debug(f"Sending command to Claude: {command[:100]}{'...' if len(command) > 100 else ''}")
```
- **Level**: DEBUG
- **When**: About to write to stdin
- **Context**: `command` (truncated)
- **Visibility**: File only

#### CB-012: Command Sent ✅
```python
# Line 67
logger.debug(f"✅ Command sent successfully")
```
- **Level**: DEBUG
- **Emoji**: ✅ (success)
- **When**: stdin.drain() completed
- **Visibility**: File only

#### CB-013: Send Failed
```python
# Line 69
logger.error(f"❌ Failed to send command: {str(e)}", exc_info=True)
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Exception during send
- **Context**: `error`
- **Extra**: Full stack trace

### Output Reading (Lines 72-99)

#### CB-014: Cannot Read
```python
# Line 75
logger.error("❌ Cannot read output - process not started")
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Attempt to read without active process
- **Result**: RuntimeError raised

#### CB-015: Starting Read
```python
# Line 78
logger.info("Starting to read Claude Code output...")
```
- **Level**: INFO
- **When**: Beginning output reading loop
- **Context**: None

#### CB-016: Process Ended
```python
# Line 85
logger.info(f"Claude process ended - read {line_count} lines total")
```
- **Level**: INFO
- **When**: stdout.readline() returns empty
- **Context**: `line_count`
- **Use**: Track total output volume

#### CB-017: Output Line 📦
```python
# Line 93
logger.debug(f"📦 Claude output [{line_count}]: {decoded_line.strip()[:100]}")
```
- **Level**: DEBUG
- **Emoji**: 📦 (output)
- **When**: Each non-empty output line
- **Context**: `line_count`, `line` (truncated)
- **Visibility**: File only
- **Frequency**: Per output line

#### CB-018: Read Error
```python
# Line 98
logger.error(f"❌ Error reading Claude output: {str(e)}", exc_info=True)
```
- **Level**: ERROR 🚨
- **Emoji**: ❌ (error)
- **When**: Exception during read
- **Context**: `error`
- **Extra**: Full stack trace

---

## Logging Configuration

**File**: `backend/src/logging_config.py`

### Configuration Settings

```python
# Default Settings (from .env)
LOG_DIR=logs
LOG_LEVEL=INFO
SQLALCHEMY_LOG_LEVEL=WARNING
```

### File Handler Configuration

```python
# Lines 45-50
rotating_handler = logging.handlers.RotatingFileHandler(
    filename=log_path,
    maxBytes=3 * 1024 * 1024,  # 3MB
    backupCount=3,  # Keep 3 backup files
    encoding='utf-8'
)
```

**Result**: 4 total files (1 active + 3 backups) = ~12MB history

### Console Handler Configuration

```python
# Lines 54-55
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
```

**Result**: Only INFO and above on console (no DEBUG spam)

### Log Format

```python
# Lines 58-61
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

**Output Example**:
```
2025-10-23 14:32:15 - src.api.websocket - INFO - [websocket.py:48] - ✅ WebSocket connection accepted - Session: abc123, User: user456
```

### SQLAlchemy Suppression

```python
# Lines 72-75
sqlalchemy_level = getattr(logging, sqlalchemy_log_level.upper(), logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(sqlalchemy_level)
logging.getLogger('sqlalchemy.engine').setLevel(sqlalchemy_level)
logging.getLogger('sqlalchemy.pool').setLevel(sqlalchemy_level)
```

**Default**: WARNING (no SQL on console)  
**Override**: Set `SQLALCHEMY_LOG_LEVEL=INFO` in `.env` to show SQL

---

## Context Variables

All log messages include relevant context for tracing:

| Variable | Type | Usage | Example |
|----------|------|-------|---------|
| `session_id` | UUID | WebSocket session identifier | `abc-123-def-456` |
| `user_id` | UUID | Authenticated user | `user-789-xyz-012` |
| `connection_id` | UUID | Specific WebSocket connection | `conn-345-uvw-678` |
| `message_id` | UUID | Saved message in database | `msg-901-rst-234` |
| `sequence_number` | int | Message ordering | `42` |
| `chunk_sequence` | int | Output chunk ordering | `15` |
| `pid` | int | Claude process ID | `12345` |
| `execution_time_ms` | int | Command duration | `3456` |
| `line_count` | int | Output line count | `127` |
| `command` | str | User command (truncated) | `"Write a Python function..."` |
| `claude_path` | str | Executable path | `/home/user/.local/bin/claude` |
| `working_directory` | str | Process CWD | `/home/user/projects/myapp` |

### Correlation Example

Tracing a single command execution through logs:

```
# 1. Connection
✅ WebSocket connection accepted - Session: abc123, User: user456

# 2. Command received
🔨 Command received - Session: abc123, Command: Write a Python function...

# 3. Sent to Claude
✅ Command sent to Claude - Session: abc123

# 4. Output streaming (file only)
📦 Output chunk [1] - Length: 50, Session: abc123
📦 Output chunk [2] - Length: 48, Session: abc123
📦 Output chunk [3] - Length: 52, Session: abc123

# 5. Complete
✅ Command execution complete - Session: abc123, Chunks: 3, Time: 1234ms
```

**All logs share `session_id: abc123`** - easy grep/filter!

---

## Log Levels Guide

### ERROR (🚨 Critical Issues)

**Visibility**: Console + File  
**When to Use**: Application errors requiring immediate attention

**Examples**:
- ❌ Failed to start Claude process
- ❌ Command execution failed
- ❌ Unexpected error in WebSocket handler
- ❌ Cannot send command - process not started

**Action**: Investigate immediately, may require operator intervention

### WARNING (⚠️ Unusual Conditions)

**Visibility**: Console + File  
**When to Use**: Suspicious but not necessarily errors

**Examples**:
- ❌ WebSocket auth failed - invalid token
- ❌ WebSocket session not found
- ❌ Invalid JSON received
- Output chunk limit reached (100 chunks)

**Action**: Monitor, may indicate client issues or attacks

### INFO (⭐ Important Events)

**Visibility**: Console + File  
**When to Use**: High-level application flow

**Examples**:
- ✅ WebSocket connection accepted
- 🔨 Command received
- ✅ Command sent to Claude
- ✅ Command execution complete
- 🔌 WebSocket disconnected

**Action**: Normal operation, good for monitoring

### DEBUG (🔍 Detailed Tracing)

**Visibility**: File only  
**When to Use**: Detailed troubleshooting information

**Examples**:
- Token verified - User: user456, Session: abc123
- 📨 WebSocket message received - Data length: 42
- 📦 Output chunk [15] - Length: 50
- User message saved - Message ID: msg123
- Connection registered - Connection ID: conn456

**Action**: Use for debugging specific issues

---

## Emoji Indicators

Emoji provide quick visual scanning of logs:

| Emoji | Meaning | When | Log Level |
|-------|---------|------|-----------|
| ✅ | Success | Operation completed successfully | INFO |
| ❌ | Error | Operation failed | ERROR/WARNING |
| 📨 | Message | WebSocket message received | DEBUG |
| 📦 | Output | Data chunk (output line) received | DEBUG |
| 🔨 | Command | User command being processed | INFO |
| 🔌 | Connection | WebSocket connected/disconnected | INFO |

**Usage in grep**:
```bash
# Find all errors
grep "❌" logs/app.log

# Find all successful operations
grep "✅" logs/app.log

# Find all commands
grep "🔨" logs/app.log

# Find connection events
grep "🔌" logs/app.log
```

---

## Performance Benchmarks

Based on typical operations:

| Operation | Expected Time | Log Points |
|-----------|--------------|------------|
| Connection establishment | 50-200ms | 5 logs |
| Command send | 10-50ms | 3 logs |
| Output streaming (per line) | 5-20ms | 1 log per line |
| Complete command cycle | 500ms-5s | 10-100+ logs |
| Disconnection | 50-100ms | 3 logs |

**Use `execution_time_ms` in WS-023 to track command performance!**

---

## Troubleshooting Quick Reference

### Problem: No logs appearing

**Check**:
1. Logs directory exists: `ls -la backend/logs/`
2. Logging initialized in `main.py`
3. Check log file: `tail -f backend/logs/app.log`

### Problem: Too many logs on console

**Check**:
1. Console handler level: Should be INFO
2. SQLAlchemy log level: `grep SQLALCHEMY_LOG_LEVEL backend/.env`
3. Debug mode accidentally enabled

### Problem: Missing context in logs

**Verify**:
1. Session ID passed to all functions
2. Logger using correct module name: `get_logger(__name__)`
3. Context variables available in scope

### Problem: Logs not rotating

**Check**:
1. File size: `ls -lh backend/logs/app.log`
2. Should rotate at 3MB
3. Backup files exist: `ls backend/logs/app.log.*`

---

## Related Documentation

- **[LOGGING_GUIDE.md](./LOGGING_GUIDE.md)** - Operator guide for configuration
- **[MESSAGE_FLOW_GUIDE.md](./tests/integration/MESSAGE_FLOW_GUIDE.md)** - Complete message flow
- **[CLAUDE_PROCESS_LIFECYCLE.md](./CLAUDE_PROCESS_LIFECYCLE.md)** - Process debugging

---

**End of Logging Reference**
