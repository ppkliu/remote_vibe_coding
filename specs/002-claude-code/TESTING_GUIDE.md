# Testing Guide: WebSocket/Claude Communication Logging

**Quick Reference for Testing the Logging Feature**

---

## Running Tests

### Unit Tests (No Database Required) ✅
```bash
cd backend
python3.12 -m pytest tests/unit/test_logging_configuration.py -v
```

**Expected Result**: 24/24 tests passing
```
Tests verify:
✅ Logging configuration basics (3 tests)
✅ Rotating file handler (5 tests)
✅ Console handler (2 tests)
✅ SQLAlchemy suppression (5 tests)
✅ Uvicorn suppression (2 tests)
✅ Logger retrieval (2 tests)
✅ Configuration validation (3 tests)
✅ Emoji support (2 tests)
```

### Integration Tests (Requires PostgreSQL)
```bash
cd backend
python3.12 -m pytest tests/integration/test_websocket_logging.py -v
```

**Note**: Tests requiring database will pass when PostgreSQL is available on localhost:5432

---

## Manual Testing: See Logs In Action

### 1. Start the Backend
```bash
cd backend
python3.12 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Startup Logs** (in console):
```
2025-10-22 20:10:49 - src.logging_config - INFO - ================================================================================
2025-10-22 20:10:49 - src.logging_config - INFO - 🚀 Claude Code Remote Web Controller - Starting
2025-10-22 20:10:49 - src.logging_config - INFO - ================================================================================
2025-10-22 20:10:49 - src.logging_config - INFO - Server: 0.0.0.0:8000
2025-10-22 20:10:49 - src.logging_config - INFO - Debug mode: True
2025-10-22 20:10:49 - src.logging_config - INFO - Claude Code: /home/image/.local/bin/claude
2025-10-22 20:10:49 - src.logging_config - INFO - Working Directory: .
2025-10-22 20:10:49 - src.logging_config - INFO - Log Directory: logs
2025-10-22 20:10:49 - src.logging_config - INFO - SQLAlchemy Log Level: WARNING
2025-10-22 20:10:49 - src.logging_config - INFO - ================================================================================
```

**Note**: No SQLAlchemy SQL queries visible ✅

### 2. Create a Session and Send a Message

#### Using Frontend
1. Open http://localhost:5173
2. Login with test credentials
3. Click "New Chat"
4. Type a message (e.g., "hello")
5. Watch the console logs

#### Using curl (if frontend not available)
```bash
# Get auth token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Create session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Authorization: Bearer YOUR_TOKEN"

# Connect to WebSocket
wscat -c "ws://localhost:8000/ws/SESSION_ID?token=YOUR_TOKEN"

# Send message
{"type":"command","command":"hello"}
```

### 3. Watch Logs Appear In This Order

**Expected Log Sequence** (console):
```
1. WebSocket connection request - Session: abc-123
2. Token verified - User: xyz-789, Session: abc-123
3. ✅ WebSocket connection accepted - Session: abc-123, User: xyz-789
4. Starting Claude process for session: abc-123
5. Claude executable path: /home/image/.local/bin/claude
6. Working directory: .
7. ✅ Claude process started successfully - PID: 12345
8. ✅ Claude process started - Session: abc-123, PID: 12345
9. 🔨 Command received - Session: abc-123, Command: hello
10. Sending command to Claude - Session: abc-123
11. ✅ Command sent to Claude - Session: abc-123
12. Starting to read Claude output...
13. 📦 Output chunk [1] - Length: 125, Session: abc-123
14. 📦 Output chunk [2] - Length: 98, Session: abc-123
... (more chunks) ...
15. ✅ Command execution complete - Session: abc-123, Chunks: 12, Time: 2543ms
16. 🔌 WebSocket disconnected - Session: abc-123, Connection: con-456
17. ✅ WebSocket cleanup complete - Session: abc-123
```

### 4. Check Log Files

**Location**: `backend/logs/app.log`

```bash
# View last 50 lines
tail -50 backend/logs/app.log

# Follow logs in real-time
tail -f backend/logs/app.log

# Search for errors
grep "❌" backend/logs/app.log

# Search for Claude process
grep "Claude process" backend/logs/app.log

# Search specific session
grep "abc-123" backend/logs/app.log
```

---

## Configuration Changes

### Disable SQLAlchemy Logging (Default)
Already configured - no action needed.

**Verify** in `.env`:
```bash
SQLALCHEMY_LOG_LEVEL=WARNING
```

### Enable SQLAlchemy Logging For Debugging
Edit `.env`:
```bash
SQLALCHEMY_LOG_LEVEL=INFO
```

Restart backend. Now console shows all SQL queries.

**Example Output**:
```
INFO:sqlalchemy.engine.Engine:BEGIN
INFO:sqlalchemy.engine.Engine:SELECT users.id, users.email FROM users WHERE users.id = %s
INFO:sqlalchemy.engine.Engine:[generated in 0.00125s] (UUID('xyz-789'),)
```

### Increase Log Verbosity
Edit `.env`:
```bash
LOG_LEVEL=DEBUG
```

Restart backend. Now console shows DEBUG logs in addition to INFO.

---

## Success Indicators

### ✅ Logging is Working Correctly If:
1. Startup logs appear immediately (< 1 second)
2. Console shows no SQL queries (unless SQLALCHEMY_LOG_LEVEL=INFO)
3. WebSocket connection logs appear within 5 seconds of connecting
4. Claude process PID appears in logs within 5 seconds
5. Command confirmation appears (✅ Command sent to Claude)
6. Output chunks logged with sequence numbers (📦 Output chunk [1], [2], etc.)
7. Execution time logged at completion
8. No errors in console (unless intentionally testing error paths)
9. Log file grows as expected (`backend/logs/app.log`)

### ❌ Common Issues:

**Problem**: Console flooded with SQL queries
- **Fix**: Verify `.env` has `SQLALCHEMY_LOG_LEVEL=WARNING`
- **Verify**: `grep SQLALCHEMY backend/.env`

**Problem**: No logs appearing
- **Fix**: Verify `LOG_DIR=logs` in `.env`
- **Fix**: Check `backend/logs/` directory exists and is writable
- **Fix**: Restart backend after changing `.env`

**Problem**: Claude process not starting
- **Fix**: Check if Claude is installed: `which claude`
- **Fix**: Check `CLAUDE_CODE_PATH` in `.env` matches actual location
- **Verify**: `ls -la /home/image/.local/bin/claude`

**Problem**: Only some logs appearing
- **Fix**: Check logger levels in code haven't been changed
- **Verify**: `grep logger src/api/websocket.py | wc -l` (should show ~18 log calls)

---

## Emoji Indicators Reference

| Emoji | Meaning | Examples |
|-------|---------|----------|
| ✅ | Success | "✅ Claude process started", "✅ Command sent" |
| ❌ | Error/Failure | "❌ Claude executable not found" |
| 📦 | Data/Package/Output | "📦 Output chunk [1]" |
| 🔨 | Action/Command | "🔨 Command received" |
| 🔌 | Connection/Network | "🔌 WebSocket disconnected" |
| 🚀 | Startup/Launch | "🚀 Claude Code Remote Web Controller - Starting" |

---

## Performance Baselines

Expected performance with proper logging configured:

| Operation | Expected Time | Logged At |
|-----------|---------------|-----------|
| WebSocket connect → acceptance | < 1 second | Immediate |
| Claude process startup | < 5 seconds | With PID |
| Command send | < 1 second | Confirmed with "✅" |
| First output chunk | 1-3 seconds | Logged with [1] |
| Total message response | < 30 seconds | Logged with total time |

---

## Debugging Tips

### 1. Trace a Specific Session
```bash
# Find session ID from logs
SESSION_ID="abc-123"

# See all logs for that session
grep "$SESSION_ID" backend/logs/app.log

# Count events per session
grep "$SESSION_ID" backend/logs/app.log | wc -l
```

### 2. Find Errors
```bash
# Show all errors with context
grep -B2 -A2 "❌" backend/logs/app.log

# Show errors with stack traces
grep -A10 "Traceback" backend/logs/app.log
```

### 3. Monitor Real-Time Activity
```bash
# Follow logs and highlight errors
tail -f backend/logs/app.log | grep -E "❌|Error|Exception"

# Follow logs and highlight success
tail -f backend/logs/app.log | grep "✅"
```

### 4. Analyze Performance
```bash
# Find all execution times
grep "execution complete" backend/logs/app.log

# Extract just the timing
grep "execution complete" backend/logs/app.log | grep -oP "Time: \d+ms"

# Calculate average
grep "execution complete" backend/logs/app.log | grep -oP '\d+(?=ms)' | awk '{sum+=$1; count++} END {print "Average:", sum/count "ms"}'
```

---

## Related Tests

- **Unit Tests**: `backend/tests/unit/test_logging_configuration.py`
- **Integration Tests**: `backend/tests/integration/test_websocket_logging.py`
- **Log Files**:
  - Main: `backend/logs/app.log`
  - Backups: `backend/logs/app.log.1`, `app.log.2`, `app.log.3`

---

## Notes

- **Database**: Tests requiring database need PostgreSQL on localhost:5432
  - Currently running at 0.0.0.0:25432 (docker-compose)
  - Update `tests/conftest.py` line 30 if using different port

- **Log Rotation**: Logs rotate at 3MB file size
  - Keeps 3 backup files (4 total)
  - ~12MB total history
  - Automatic cleanup - no manual intervention needed

- **UTF-8 Encoding**: All log files use UTF-8
  - Emoji and special characters supported
  - Safe for unicode logging

---

## Further Reading

- **Specification**: `/specs/002-claude-code/spec.md`
- **Implementation Summary**: `/specs/002-claude-code/IMPLEMENTATION_SUMMARY.md`
- **Logging Config**: `backend/src/logging_config.py`
- **WebSocket Handler**: `backend/src/api/websocket.py`
- **Claude Bridge**: `backend/src/services/claude_bridge.py`
