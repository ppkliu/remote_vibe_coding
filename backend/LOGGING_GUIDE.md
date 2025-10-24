# Logging & Debugging Guide

## Overview

This guide helps operators understand, configure, and troubleshoot logging in the Claude Code Remote Web Controller.

**TL;DR**: By default, console shows clean application logs (no SQL), and everything is saved to `logs/app.log`. To see SQL queries, set `SQLALCHEMY_LOG_LEVEL=INFO` in `.env` and restart.

## Quick Summary

| Setting | Default | Purpose |
|---------|---------|---------|
| Console Output | INFO level | High-level application events |
| File Output | DEBUG level | Complete history with details |
| SQL Logging | WARNING (hidden) | Don't spam console with SQL |
| Log File | `logs/app.log` | Rotating file handler (3MB × 3) |

## Default Behavior (Out of the Box)

```bash
# In .env:
LOG_DIR=logs
LOG_LEVEL=INFO
SQLALCHEMY_LOG_LEVEL=WARNING
```

**Result**:
- ✅ Console: Clean, readable application events
- ✅ File: Complete history with DEBUG details
- ✅ No SQL on console
- ✅ SQL still available in log files if needed

## Console Output (What You See)

```
2025-10-23 14:32:10 - src.api.websocket - INFO - ✅ WebSocket connection accepted - Session: abc123
2025-10-23 14:32:13 - src.services.claude_bridge - INFO - ✅ Claude Code process started successfully - PID: 12345
2025-10-23 14:32:15 - src.api.websocket - INFO - ✅ Command sent to Claude - Session: abc123
2025-10-23 14:32:16 - src.api.websocket - INFO - 📦 Output chunk [1] - Length: 50, Session: abc123
2025-10-23 14:32:16 - src.api.websocket - INFO - ✅ Command execution complete - Session: abc123
```

### Log Format

```
TIMESTAMP - LOGGER_NAME - LEVEL - MESSAGE
```

- **TIMESTAMP**: When event occurred (YYYY-MM-DD HH:MM:SS)
- **LOGGER_NAME**: Which module logged it (websocket, claude_bridge, etc.)
- **LEVEL**: INFO/WARNING/ERROR
- **MESSAGE**: What happened + context (session_id, user_id, etc.)

## Enabling SQL Logging

### When to Enable

- Debugging slow database queries
- Performance analysis
- Understanding database access patterns
- Investigating database-related errors

### How to Enable

**Step 1**: Edit `.env`
```bash
cd backend
vim .env  # or nano, vi, etc.
```

**Step 2**: Find or add this line:
```
SQLALCHEMY_LOG_LEVEL=INFO
```

(Set to `DEBUG` for even more detail including parameter values)

**Step 3**: Restart backend
```bash
# If running with hot-reload (Ctrl+C stops it)
python3.12 -m uvicorn src.main:app --reload

# Or restart in another terminal if it's running in background
```

**Step 4**: Verify
```bash
tail -f logs/app.log | grep "SELECT\|INSERT"
# Should show SQL queries now
```

### Example: What SQL Logging Shows

```
2025-10-23 14:32:15 - sqlalchemy.engine - DEBUG - SELECT "users"."id", "users"."email" FROM "users"
WHERE "users"."id" = %(user_id_1)s [{'user_id_1': '123e456...'}]

2025-10-23 14:32:15 - sqlalchemy.engine - DEBUG - INSERT INTO "messages" ("session_id", "role", "content", "created_at")
VALUES (%(session_id_1)s, %(role_1)s, %(content_1)s, %(created_at_1)s)
```

## Log Files

### Location and Size

```
logs/app.log         (current, up to 3MB)
logs/app.log.1       (backup, 3MB)
logs/app.log.2       (backup, 3MB)
logs/app.log.3       (backup, 3MB)
Total: ~12MB history
```

Automatically rotates when reaching 3MB.

### Managing Log Files

```bash
# View recent errors
tail -50 logs/app.log | grep -i error

# Archive old logs
tar czf logs-backup-$(date +%Y%m%d).tar.gz logs/app.log.*

# Clear old backups
rm logs/app.log.[123]
```

## Troubleshooting

### Problem: SQL appearing on console when it shouldn't

**Check**:
```bash
grep SQLALCHEMY_LOG_LEVEL backend/.env
echo $SQLALCHEMY_LOG_LEVEL
```

**Fix**: Set to `WARNING`, restart backend

### Problem: Not seeing detailed logs

**Check if backend restarted after changing .env**:
```bash
# Stop backend (Ctrl+C)
# Start again:
python3.12 -m uvicorn src.main:app --reload
```

**Verify settings took effect**:
```bash
grep -E "Log Level|SQLAlchemy" logs/app.log | head -5
```

### Problem: Log file too large

The rotation is automatic. To manually manage:

```bash
# Check size
ls -lh logs/app.log*

# Archive if needed
tar czf logs/archive-$(date +%Y%m%d).tar.gz logs/app.log.*
rm logs/app.log.[123]
```

## Emoji Indicators (Quick Reference)

| Symbol | Meaning | When |
|--------|---------|------|
| ✅ | Success | Operation completed successfully |
| ❌ | Error | Operation failed |
| 📨 | Message | WebSocket message received |
| 📦 | Output | Data chunk (output line) received |
| 🔨 | Command | User command being processed |
| 🔌 | Connection | WebSocket connected/disconnected |

## Log Levels

| Level | Shown on Console | Purpose |
|-------|-----------------|---------|
| **ERROR** | Yes | Application errors that require attention |
| **WARNING** | Yes | Unusual conditions (not necessarily errors) |
| **INFO** | Yes | Important application events (default) |
| **DEBUG** | No (file only) | Detailed troubleshooting information |

## Performance Troubleshooting

```bash
# Look for slow executions
grep "Command execution complete" logs/app.log | grep -E "[3-9][0-9][0-9][0-9][0-9]ms"

# Example:
# ✅ Command execution complete - Session: abc123, Chunks: 3, Time: 45678ms
#                                                             ^^^^^^^ 45+ seconds!
```

**What to check if slow**:
1. Verify Claude is responding: `ps aux | grep claude`
2. Check system resources: `top`
3. Enable SQL logging to see database queries
4. Check network connectivity

## Configuration Reference

All in `backend/.env`:

```bash
LOG_DIR=logs                    # Where to save log files
LOG_LEVEL=INFO                  # Console log level (INFO by default)
SQLALCHEMY_LOG_LEVEL=WARNING    # SQL logging (WARNING = suppressed, INFO = show)

# To show SQL:
SQLALCHEMY_LOG_LEVEL=INFO

# To show SQL with parameters:
SQLALCHEMY_LOG_LEVEL=DEBUG
```

## Related Documentation

- [MESSAGE_FLOW_GUIDE.md](./tests/integration/MESSAGE_FLOW_GUIDE.md) - Complete message flow
- [CLAUDE_PROCESS_LIFECYCLE.md](./CLAUDE_PROCESS_LIFECYCLE.md) - Process debugging
- [LOGGING_REFERENCE.md](./LOGGING_REFERENCE.md) - All logging points (if exists)
