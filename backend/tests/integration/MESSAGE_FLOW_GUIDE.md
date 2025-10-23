# Message Flow Guide - WebSocket to Claude Code

## Overview

This guide explains how messages flow through the system from a user's chat interface to Claude Code execution and back, including all logging checkpoints that help with debugging.

## Complete Message Flow Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER SENDS MESSAGE                                           │
│    Frontend: POST /api/v1/sessions/{id}/messages                │
│    Payload: { type: "command", command: "echo 'hello'" }        │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. WEBSOCKET CONNECTION PHASE                                   │
│    Client: Connect to /ws/{session_id}?token={jwt}              │
│                                                                 │
│    Logs:                                                        │
│    - WebSocket connection request - Session: {id}              │
│    - Token verified - User: {id}, Session: {id}                │
│    - ✅ WebSocket connection accepted                          │
│    - Connection registered - Connection ID: {id}               │
│                                                                 │
│    Timing: 1-2 seconds from connection request                 │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. CLAUDE PROCESS STARTUP PHASE                                 │
│    If not already running, start new process                    │
│                                                                 │
│    Logs:                                                        │
│    - Starting Claude Code process                              │
│    - Claude executable path: /home/user/.local/bin/claude       │
│    - Working directory: .                                       │
│    - ✅ Claude Code process started successfully - PID: 12345   │
│                                                                 │
│    Timing: 3-5 seconds (if starting new process)                │
│    OR: < 1 second (if reusing existing process)                │
│                                                                 │
│    Error Logs (if startup fails):                              │
│    - ❌ File not found error: Claude executable not found       │
│    - ❌ Failed to start Claude Code process: ...                │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. MESSAGE RECEPTION                                            │
│    WebSocket receives user command                              │
│                                                                 │
│    Logs:                                                        │
│    - 📨 WebSocket message received - Session: {id}             │
│    - Message type: command - Session: {id}                     │
│    - 🔨 Command received - Session: {id}, Command: echo...      │
│    - User message saved - Message ID: {id}                     │
│                                                                 │
│    Timing: < 100ms                                              │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. COMMAND SENDING PHASE                                        │
│    Send command to Claude Code stdin                            │
│                                                                 │
│    Logs:                                                        │
│    - Sending command to Claude - Session: {id}                 │
│    - Sending command to Claude: echo 'hello'...                │
│    - ✅ Command sent successfully                               │
│    - ✅ Command sent to Claude - Session: {id}                 │
│                                                                 │
│    Timing: 1-2 seconds                                          │
│    Total elapsed: 5-10 seconds from WebSocket connect           │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. OUTPUT READING PHASE                                         │
│    Stream output from Claude Code stdout                        │
│                                                                 │
│    Logs (repeated for each output line):                       │
│    - Starting to read Claude Code output...                    │
│    - 📦 Claude output [1]: hello                               │
│    - 📦 Claude output [2]: next line of output                 │
│    - 📦 Claude output [3]: another output line                 │
│    ...                                                          │
│    - Claude process ended - read 3 lines total                 │
│                                                                 │
│    WebSocket Sends (for each line):                            │
│    - { type: "output_chunk", sequence: 1, content: "..." }    │
│    - { type: "output_chunk", sequence: 2, content: "..." }    │
│    - { type: "output_chunk", sequence: 3, content: "..." }    │
│                                                                 │
│    Timing: 1-5 seconds (depends on Claude execution)           │
│    Total elapsed: 10-20 seconds from initial connection        │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. EXECUTION COMPLETION                                         │
│    All output received, command execution complete              │
│                                                                 │
│    Logs:                                                        │
│    - ✅ Command execution complete - Session: {id},            │
│      Chunks: 3, Time: 1234ms                                    │
│    - Assistant response saved - Message ID: {id}               │
│                                                                 │
│    WebSocket Sends:                                            │
│    - { type: "command_complete",                              │
│        execution_time_ms: 1234,                                │
│        chunks_count: 3 }                                        │
│                                                                 │
│    Timing: Immediate after output reading completes            │
│    Total elapsed: 10-25 seconds from initial connection        │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. DISCONNECTION (Optional)                                     │
│    When user closes chat or closes WebSocket                    │
│                                                                 │
│    Logs:                                                        │
│    - 🔌 WebSocket disconnected - Session: {id}, Connection: {id}│
│    - ✅ WebSocket cleanup complete - Session: {id}             │
│                                                                 │
│    Timing: On user action                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Error Scenarios

### Scenario 1: Missing Claude Executable

```
Logs:
❌ File not found error: Claude executable not found at: /path/to/claude
❌ Failed to start Claude Code process: Failed to start Claude Code: ...

WebSocket Response:
{ type: "error", content: "Failed to start process: Claude executable not found..." }

Timing: ~2-5 seconds (after trying to start)
Action: User sees error, can check Claude installation
```

### Scenario 2: Claude Process Crashes

```
Logs:
✅ Command sent to Claude - Session: {id}
Starting to read Claude Code output...
❌ Error reading Claude output: ...
❌ Command execution failed - Session: {id}, Error: ...

WebSocket Response:
{ type: "error", content: "Command execution failed: Process crashed..." }

Timing: Varies, usually within 30 seconds
Action: User sees error, backend logs show crash details
```

### Scenario 3: WebSocket Disconnection During Execution

```
Logs:
✅ Command sent to Claude - Session: {id}
Starting to read Claude Code output...
📦 Claude output [1]: first line
🔌 WebSocket disconnected - Session: {id}, Connection: {id}
❌ Unexpected error in WebSocket handler - Session: {id}, Error: Connection lost

Timing: Variable (when user closes browser/tab)
Action: Client connection closes, resources cleaned up
```

### Scenario 4: Invalid Message Format

```
Logs:
📨 WebSocket message received - Session: {id}, Data length: 45
❌ Invalid JSON received - Session: {id}

WebSocket Response:
{ type: "error", content: "Invalid JSON" }

Timing: < 100ms
Action: User sees error, can retry with correct format
```

## Logging Levels and Filtering

### INFO Level (Default - Console Output)
Shows high-level flow:
- Connection acceptance
- Process startup
- Command sending/completion
- Errors and warnings

```
Use case: Operators monitoring the system in real-time
Filter: grep -E "INFO|WARNING|ERROR" app.log
```

### DEBUG Level (File Only - Not on Console)
Detailed flow for troubleshooting:
- Message reception
- Output chunk details
- Token verification
- Database operations
- Resource cleanup

```
Use case: Developers debugging specific issues
Filter: grep DEBUG app.log | grep session_id
```

### ERROR Level (Always Visible)
System errors and crashes:
- Failed startup
- Crashed processes
- Unexpected exceptions
- Stack traces (with exc_info=True)

```
Use case: Critical issue detection
Filter: grep ERROR app.log
```

## Expected Timing Benchmarks

| Phase | Expected Time | Status | Action |
|-------|---------------|--------|--------|
| WebSocket connection | 1-2s | Normal | Connection accepted log |
| Claude startup (new process) | 3-5s | Normal | "Claude process started" log |
| Claude startup (existing) | < 1s | Better | "Using existing Claude bridge" log |
| Command sending | 1-2s | Normal | "Command sent to Claude" log |
| Output reading | 1-5s | Variable | "Output chunk" logs |
| Total (first message) | 10-25s | Normal | "execution complete" log with time |
| Total (subsequent messages) | 5-20s | Better | Faster when process already running |

### Performance Red Flags

- WebSocket connection > 5s → Check token verification, database
- Claude startup > 10s → Check executable path, system resources
- Command sending > 5s → Check stdin buffer, subprocess state
- Total execution > 60s → Check for hung processes, database locks
- No response after 30s → Check logs for "ERROR" entries

## Log Examples

### Successful Complete Flow Log Excerpt

```
2025-10-23 14:32:10 - src.api.websocket - INFO - WebSocket connection request - Session: abc123
2025-10-23 14:32:10 - src.api.websocket - DEBUG - Token verified - User: user456, Session: abc123
2025-10-23 14:32:10 - src.api.websocket - INFO - ✅ WebSocket connection accepted - Session: abc123, User: user456
2025-10-23 14:32:11 - src.api.websocket - INFO - No active Claude bridge found, starting new process - Session: abc123
2025-10-23 14:32:13 - src.services.claude_bridge - INFO - Starting Claude Code process
2025-10-23 14:32:13 - src.services.claude_bridge - INFO - Claude executable path: /home/user/.local/bin/claude
2025-10-23 14:32:13 - src.services.claude_bridge - INFO - Working directory: .
2025-10-23 14:32:14 - src.services.claude_bridge - INFO - ✅ Claude Code process started successfully - PID: 12345
2025-10-23 14:32:15 - src.api.websocket - INFO - ✅ Claude process started successfully - Session: abc123
2025-10-23 14:32:16 - src.api.websocket - DEBUG - 📨 WebSocket message received - Session: abc123, Data length: 42
2025-10-23 14:32:16 - src.api.websocket - DEBUG - Message type: command - Session: abc123
2025-10-23 14:32:16 - src.api.websocket - INFO - 🔨 Command received - Session: abc123, Command: echo 'hello'
2025-10-23 14:32:16 - src.api.websocket - DEBUG - User message saved - Message ID: msg789
2025-10-23 14:32:16 - src.api.websocket - INFO - Sending command to Claude - Session: abc123
2025-10-23 14:32:17 - src.services.claude_bridge - DEBUG - Sending command to Claude: echo 'hello'
2025-10-23 14:32:17 - src.services.claude_bridge - DEBUG - ✅ Command sent successfully
2025-10-23 14:32:17 - src.api.websocket - INFO - ✅ Command sent to Claude - Session: abc123
2025-10-23 14:32:17 - src.api.websocket - INFO - Starting to read Claude output - Session: abc123
2025-10-23 14:32:17 - src.services.claude_bridge - INFO - Starting to read Claude Code output...
2025-10-23 14:32:18 - src.services.claude_bridge - DEBUG - 📦 Claude output [1]: hello
2025-10-23 14:32:18 - src.api.websocket - DEBUG - 📦 Output chunk [1] - Length: 6, Session: abc123
2025-10-23 14:32:18 - src.services.claude_bridge - INFO - Claude process ended - read 1 lines total
2025-10-23 14:32:18 - src.api.websocket - INFO - ✅ Command execution complete - Session: abc123, Chunks: 1, Time: 1234ms
2025-10-23 14:32:18 - src.api.websocket - DEBUG - Assistant response saved - Message ID: msg790
```

### Error Flow Log Excerpt

```
2025-10-23 14:32:10 - src.api.websocket - INFO - ✅ WebSocket connection accepted - Session: abc123
2025-10-23 14:32:11 - src.api.websocket - INFO - No active Claude bridge found, starting new process - Session: abc123
2025-10-23 14:32:12 - src.services.claude_bridge - INFO - Starting Claude Code process
2025-10-23 14:32:12 - src.services.claude_bridge - INFO - Claude executable path: /invalid/path/claude
2025-10-23 14:32:12 - src.services.claude_bridge - ERROR - Claude executable not found at: /invalid/path/claude
2025-10-23 14:32:12 - src.services.claude_bridge - ERROR - ❌ File not found error: Claude executable not found at: /invalid/path/claude
2025-10-23 14:32:12 - src.services.claude_bridge - ERROR - ❌ Failed to start Claude Code process: ...
Traceback (most recent call last):
  ...
FileNotFoundError: Claude executable not found
2025-10-23 14:32:12 - src.api.websocket - ERROR - ❌ Failed to start Claude process - Session: abc123, Error: Failed to start Claude Code: ...
2025-10-23 14:32:12 - src.api.websocket - ERROR - Exception trace: ... full stack trace ...
```

## Interpreting Logs for Troubleshooting

### Q: User says "I got no response"

**Check these logs in order:**

1. Look for "WebSocket connection accepted" ✅
   - If NOT found → Connection failed, check token/session
   - If found → Continue to next check

2. Look for "Claude Code process started" ✅
   - If NOT found → Check "Failed to start Claude process" ❌
   - If found → Continue to next check

3. Look for "Command sent to Claude" ✅
   - If NOT found → Check "Sending command to Claude" for errors
   - If found → Continue to next check

4. Look for "Command execution complete" ✅
   - If NOT found → Check for "Error reading Claude output" ❌
   - If found → Message was processed, check if frontend received it

5. **Result:**
   - If command_complete is missing → Frontend didn't receive response (network issue?)
   - If output_chunk is present but no command_complete → Output was cut off
   - If no output_chunk → Claude produced no output (valid for some commands)

### Q: "Command execution took forever"

**Check execution time in logs:**

```
✅ Command execution complete - Session: abc123, Chunks: 3, Time: 45000ms
                                                                    ^^^^^^
                                                              Look at time here
```

- < 1000ms (< 1s) → Very fast, likely mock or cached
- 1000-5000ms (1-5s) → Normal
- 5000-30000ms (5-30s) → Slow but acceptable
- > 30000ms (> 30s) → Very slow, investigate
  - Check if Claude is actually responding
  - Check system resources (CPU, memory)
  - Check database load

### Q: "I see SQL logs on the console"

**This shouldn't happen, but if it does:**

```bash
# Check environment variable
echo $SQLALCHEMY_LOG_LEVEL  # Should print: WARNING

# Check configuration
grep SQLALCHEMY_LOG_LEVEL .env

# Restart backend
# SQLAlchemy logging is read at startup

# Verify in logs
grep sqlalchemy app.log | wc -l  # Should be 0 or very low
```

## Related Documentation

- [LOGGING_REFERENCE.md](./LOGGING_REFERENCE.md) - Complete logging reference
- [CLAUDE_PROCESS_LIFECYCLE.md](./CLAUDE_PROCESS_LIFECYCLE.md) - Process lifecycle details
- [WEBSOCKET_DEBUG_GUIDE.md](./WEBSOCKET_DEBUG_GUIDE.md) - WebSocket troubleshooting
