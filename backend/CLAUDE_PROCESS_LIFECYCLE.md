# Claude Process Lifecycle Debugging Guide

## Overview

This guide documents the complete lifecycle of a Claude Code process from startup through execution to cleanup, with logging checkpoints that help operators debug communication issues.

## Process Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. PROCESS STARTUP PHASE                                            │
│                                                                     │
│ Logs:                                                               │
│ - Starting Claude Code process                                     │
│ - Claude executable path: /home/user/.local/bin/claude              │
│ - Working directory: .                                              │
│ - Creating subprocess with: ...                                     │
│ - ✅ Claude Code process started successfully - PID: 12345          │
│                                                                     │
│ Timing: 2-5 seconds                                                 │
│ Files: src/services/claude_bridge.py (L22-47)                       │
└─────────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. PROCESS READY PHASE                                              │
│                                                                     │
│ State:                                                              │
│ - Process initialized with PID                                     │
│ - stdin: Ready for input                                           │
│ - stdout: Waiting for output                                       │
│ - stderr: Monitoring for errors                                    │
│                                                                     │
│ Logs:                                                               │
│ - No additional logs (process is idle)                             │
│                                                                     │
│ Timing: Immediate after startup                                    │
└─────────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. COMMAND SENDING PHASE                                            │
│                                                                     │
│ Logs:                                                               │
│ - Sending command to Claude: echo 'hello'                          │
│ - ✅ Command sent successfully                                     │
│                                                                     │
│ Timing: <1 second                                                   │
│ Files: src/services/claude_bridge.py (L57-70)                       │
└─────────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. OUTPUT READING PHASE                                             │
│                                                                     │
│ Logs (for each output line):                                       │
│ - Starting to read Claude Code output...                           │
│ - 📦 Claude output [1]: hello                                      │
│ - 📦 Claude output [2]: next line                                  │
│ - 📦 Claude output [3]: another line                               │
│ - Claude process ended - read 3 lines total                        │
│                                                                     │
│ Timing: 1-5 seconds (varies with command)                          │
│ Files: src/services/claude_bridge.py (L72-99)                       │
└─────────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. CLEANUP PHASE                                                    │
│                                                                     │
│ State:                                                              │
│ - Process terminates naturally or is killed                        │
│ - stdin/stdout/stderr file handles closed                          │
│ - Process resources released                                       │
│                                                                     │
│ Logs:                                                               │
│ - (Implicit cleanup on disconnection)                              │
│ - ✅ WebSocket cleanup complete - Session: {id}                    │
│                                                                     │
│ Timing: Immediate on disconnection or after final output           │
│ Files: src/api/websocket.py (L244-251)                              │
└─────────────────────────────────────────────────────────────────────┘
```

## Error Paths

### Error 1: Executable Not Found

```
Logs:
Starting Claude Code process
Claude executable path: /invalid/path/claude
Working directory: .
Claude executable not found at: /invalid/path/claude
❌ File not found error: Claude executable not found at: /invalid/path/claude
❌ Failed to start Claude Code process: Failed to start Claude Code: ...

Traceback (most recent call last):
  File "src/services/claude_bridge.py", line 28, in start_process
    if not os.path.exists(self.claude_path):
...
FileNotFoundError: Claude executable not found at: /invalid/path/claude

Timing: ~2-3 seconds (fails fast)
Action: Check CLAUDE_CODE_PATH environment variable
        Check that Claude is installed: which claude
        Verify file exists and is executable: chmod +x /path/to/claude
```

### Error 2: Working Directory Missing

```
Logs:
Starting Claude Code process
Claude executable path: /home/user/.local/bin/claude
Working directory: /invalid/directory
Working directory does not exist: /invalid/directory
❌ File not found error: Working directory does not exist: /invalid/directory
❌ Failed to start Claude Code process: ...

Timing: ~1-2 seconds
Action: Check CLAUDE_WORKING_DIRECTORY environment variable
        Verify directory exists: ls -ld /path/to/directory
        Create directory if needed: mkdir -p /path/to/directory
```

### Error 3: Process Crashes During Output Reading

```
Logs:
✅ Claude Code process started successfully - PID: 12345
Sending command to Claude: echo 'test'
✅ Command sent successfully
Starting to read Claude Code output...
📦 Claude output [1]: hello
❌ Error reading Claude output: Broken pipe
Claude process ended - read 1 lines total

Timing: 1-5 seconds after command send
Action: Check if Claude process crashed (external monitoring)
        Review /tmp/claude-debug.log if available
        Check system resources (disk space, memory)
        Try killing the process and starting fresh: pkill claude
```

### Error 4: Command Execution Timeout

```
Logs:
✅ Claude Code process started successfully - PID: 12345
Sending command to Claude: long-running-command
✅ Command sent successfully
Starting to read Claude Code output...
(waiting for 30+ seconds with no output)
⏱️ Command execution timeout - waiting >30 seconds for response

Timing: 30+ seconds
Action: Check if Claude is hung: ps aux | grep claude
        Check for infinite loops in command
        Kill process if stuck: kill -9 12345
        Restart Claude: restart backend
```

## Log Entry Examples

### Successful Process Lifecycle

```
2025-10-23 14:32:13 - src.api.websocket - INFO - Starting Claude Code process
2025-10-23 14:32:13 - src.services.claude_bridge - INFO - Starting Claude Code process
2025-10-23 14:32:13 - src.services.claude_bridge - INFO - Claude executable path: /home/user/.local/bin/claude
2025-10-23 14:32:13 - src.services.claude_bridge - INFO - Working directory: .
2025-10-23 14:32:13 - src.services.claude_bridge - DEBUG - Creating subprocess with: /home/user/.local/bin/claude
2025-10-23 14:32:14 - src.services.claude_bridge - INFO - ✅ Claude Code process started successfully - PID: 12345
2025-10-23 14:32:15 - src.api.websocket - INFO - Sending command to Claude - Session: abc123
2025-10-23 14:32:15 - src.services.claude_bridge - DEBUG - Sending command to Claude: echo 'hello'
2025-10-23 14:32:15 - src.services.claude_bridge - DEBUG - ✅ Command sent successfully
2025-10-23 14:32:15 - src.api.websocket - INFO - Starting to read Claude output - Session: abc123
2025-10-23 14:32:15 - src.services.claude_bridge - INFO - Starting to read Claude Code output...
2025-10-23 14:32:16 - src.services.claude_bridge - DEBUG - 📦 Claude output [1]: hello
2025-10-23 14:32:16 - src.api.websocket - DEBUG - 📦 Output chunk [1] - Length: 6, Session: abc123
2025-10-23 14:32:16 - src.services.claude_bridge - INFO - Claude process ended - read 1 lines total
2025-10-23 14:32:16 - src.api.websocket - INFO - ✅ Command execution complete - Session: abc123, Chunks: 1, Time: 1234ms
```

## Debugging Process Lifecycle Issues

### Symptom: "Process never starts"

**Check these logs in order**:

1. Look for "Starting Claude Code process"
   - If NOT found → WebSocket handler not reaching process start code
   - Check connection was accepted (look for "✅ WebSocket connection accepted")

2. Look for "Claude executable path"
   - If NOT found → Something crashed before reaching path check
   - Check logs for exceptions above this point

3. Look for "❌ File not found error"
   - If found → CLAUDE_CODE_PATH is incorrect
   - Fix: Check `echo $CLAUDE_CODE_PATH` and `which claude`

4. Look for "❌ Working directory does not exist"
   - If found → CLAUDE_WORKING_DIRECTORY is incorrect
   - Fix: Check `echo $CLAUDE_WORKING_DIRECTORY` and `ls -d` it

5. Look for "✅ Claude Code process started successfully"
   - If NOT found → Check system resources (disk, memory, file limits)
   - Try: `ulimit -a` and compare with process startup requirements

### Symptom: "Process starts but produces no output"

**Check these logs**:

1. Look for "✅ Claude Code process started successfully - PID: XXXX"
   - If found → Process is running

2. Verify the PID still exists:
   ```bash
   ps -p XXXX  # Should show the claude process
   ```

3. Look for "Starting to read Claude Code output..."
   - If NOT found → Process may have crashed immediately
   - If found → Process is running, waiting for output

4. Check if command was sent:
   ```
   grep "Sending command to Claude" app.log
   grep "✅ Command sent successfully" app.log
   ```

5. Check process output manually:
   ```bash
   # Run the command directly
   /home/user/.local/bin/claude <<< "echo 'test'"

   # See if it produces output
   ```

### Symptom: "Process crashes mid-execution"

**Check these logs**:

```
1. Process starts successfully ✅
2. Command sent successfully ✅
3. Starting to read Claude Code output...
4. 📦 Claude output [1]: (some output)
5. ❌ Error reading Claude output: (error details)
```

**What to investigate**:
- Check system resources during execution:
  ```bash
  top -p XXXX  # Monitor the process
  ```

- Check if output is being written:
  ```bash
  strace -p XXXX 2>&1 | grep write  # Trace system calls
  ```

- Check for segmentation faults:
  ```bash
  dmesg | tail -20  # Look for segfault entries
  ```

## Performance Benchmarks

| Event | Expected Time | Acceptable Range | Red Flag |
|-------|---|---|---|
| Process startup | 3-5s | 2-10s | >10s |
| Command sending | 1s | <2s | >5s |
| Output line reading | 100-500ms | <1s | >5s per line |
| Total execution | 10-30s | 5-60s | >60s |

## Key Files for Debugging

| File | Purpose | Key Functions |
|------|---------|---|
| `src/services/claude_bridge.py` | Process management | `start_process()`, `send_command()`, `read_output()` |
| `src/api/websocket.py` | WebSocket handling | WebSocket handler, message routing |
| `src/logging_config.py` | Logging setup | `setup_logging()` configuration |
| `logs/app.log` | Main log file | All process lifecycle events |

## Environment Variables

| Variable | Purpose | Example | Check |
|----------|---------|---------|-------|
| `CLAUDE_CODE_PATH` | Path to Claude executable | `/home/user/.local/bin/claude` | `which claude` |
| `CLAUDE_WORKING_DIRECTORY` | Working directory for Claude | `.` or `/home/user/project` | `ls -d $DIR` |
| `LOG_DIR` | Directory for log files | `logs` | `ls -d $LOG_DIR` |
| `SQLALCHEMY_LOG_LEVEL` | Database logging level | `WARNING` | See in logs |

## Related Documentation

- [MESSAGE_FLOW_GUIDE.md](./tests/integration/MESSAGE_FLOW_GUIDE.md) - Complete message flow
- [LOGGING_REFERENCE.md](./LOGGING_REFERENCE.md) - All logging points
- [WEBSOCKET_DEBUG_GUIDE.md](./WEBSOCKET_DEBUG_GUIDE.md) - WebSocket troubleshooting
