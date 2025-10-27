# Operational Runbook: WebSocket/Claude Code Logging

**Feature**: 002-claude-code - Debug and Fix WebSocket/Claude Code Communication  
**Last Updated**: 2025-10-25  
**Version**: 1.0.0

---

## Quick Reference

| Scenario | Action | Reference |
|----------|--------|-----------|
| User sends message but no response | Check logs for session_id | [Troubleshooting: No Response](#troubleshooting-no-response) |
| Backend running slowly | Enable SQL logging temporarily | [Performance Debugging](#performance-debugging) |
| Claude process won't start | Check executable path in logs | [Troubleshooting: Process Won't Start](#troubleshooting-process-wont-start) |
| Need to trace user message | Grep logs with session_id | [Log Tracing](#log-tracing) |
| Running out of disk space | Archive old logs | [Log Management](#log-management) |

---

## Daily Operations

### Morning Health Check

```bash
# SSH into backend server
ssh backend-server

# Check if backend is running
docker ps | grep backend
# OR
systemctl status claude-backend

# Check log file size
du -h /var/log/claude-backend/app.log

# Check recent errors
tail -50 /var/log/claude-backend/app.log | grep -i error

# Verify logging configuration
grep -E "LOG_LEVEL|SQLALCHEMY" /etc/claude-backend/.env
```

**Expected Results**:
- ✅ Backend container running or service active
- ✅ Log file < 3GB (should be ~100MB with rotation)
- ✅ No critical errors in recent logs
- ✅ SQLALCHEMY_LOG_LEVEL=WARNING (or INFO if debugging)

### Evening Summary

```bash
# Count messages processed today
grep "Command execution complete" /var/log/claude-backend/app.log | wc -l

# Find slowest messages
grep "Command execution complete" /var/log/claude-backend/app.log | \
  grep -oP 'Time: \K\d+' | sort -rn | head -5

# Check for failed processes
grep "❌ Failed\|ERROR" /var/log/claude-backend/app.log | wc -l

# Verify no database issues
grep "database\|connection\|unavailable" /var/log/claude-backend/app.log -i
```

---

## Troubleshooting Guide

### Troubleshooting: No Response

**Problem**: User sent message, backend shows no logs  
**Time to Resolve**: 2-5 minutes

#### Step 1: Verify Backend Running

```bash
# Check if backend is running
curl http://localhost:8000/health || echo "Backend not responding"

# Check logs
tail -20 /var/log/claude-backend/app.log
```

**What to look for**:
- ✅ Recent startup logs
- ❌ "Connection refused" → Backend not running
- ❌ "error" → Check error details

#### Step 2: Check WebSocket Connection

```bash
# Get session ID from frontend (user provides or check browser)
SESSION_ID="abc-123-def-456"

# Search logs for session
grep "$SESSION_ID" /var/log/claude-backend/app.log

# Should show:
# - "WebSocket connection request"
# - "✅ WebSocket connection accepted"
# - "🔨 Command received"
```

**If no logs appear**: 
- WebSocket connection never established
- Check firewall, network connectivity
- Verify authentication token valid

#### Step 3: Check Claude Process

```bash
# Look for Claude startup
grep "Claude process" /var/log/claude-backend/app.log | tail -5

# If process failed to start
grep "❌ Failed to start\|not found\|executable" /var/log/claude-backend/app.log

# Check Claude is installed
which claude
ls -la /path/to/claude
```

**If Claude not found**:
- Verify installation: `which claude`
- Update CLAUDE_CODE_PATH in .env
- Restart backend

#### Step 4: Check Command Sending

```bash
# Search for command in logs
grep "🔨 Command received\|✅ Command sent" /var/log/claude-backend/app.log | tail -5

# If "received" but no "sent":
grep "❌ Command execution\|error" /var/log/claude-backend/app.log
```

**Common Issues**:
| Log Entry | Meaning | Action |
|-----------|---------|--------|
| "Command received" only | Command wasn't sent to Claude | Check Claude bridge error |
| "Command sent" only | Claude hanging, check timeout | Check system resources |
| Both + no output | Claude processing slowly | Wait longer or check Claude logs |

#### Step 5: Enable SQL Logging (If Still Stuck)

```bash
# Temporarily enable SQL logging
echo "SQLALCHEMY_LOG_LEVEL=INFO" >> /etc/claude-backend/.env

# Restart backend
systemctl restart claude-backend
# OR
docker-compose restart backend

# Retry operation
# Check if database issue is cause
grep "SELECT\|INSERT\|database" /var/log/claude-backend/app.log -i | tail -20
```

**Resolution Actions**:
- ✅ Message appears in logs → User can see it works
- ✅ Database error → Fix database connection
- ✅ Claude timeout → Check Claude process/resources
- ✅ Network issue → Check firewall/connectivity

---

### Troubleshooting: Process Won't Start

**Problem**: "❌ Claude process failed to start"  
**Time to Resolve**: 3-10 minutes

#### Step 1: Check Error Message

```bash
tail -30 /var/log/claude-backend/app.log | grep -A 5 "❌"
```

**Common Errors**:

| Error | Cause | Fix |
|-------|-------|-----|
| "Claude executable not found" | Path incorrect or not installed | Install Claude or fix CLAUDE_CODE_PATH |
| "Working directory does not exist" | Invalid CLAUDE_WORKING_DIRECTORY | Create directory or update .env |
| "Permission denied" | Claude not executable | `chmod +x /path/to/claude` |
| "No such file or directory" | Binary corrupted or wrong path | Reinstall Claude |

#### Step 2: Verify Installation

```bash
# Check Claude path
echo $CLAUDE_CODE_PATH
# OR check .env
grep CLAUDE_CODE_PATH /etc/claude-backend/.env

# Test executable
/path/to/claude --version

# If not executable
chmod +x /path/to/claude

# If missing
which claude
```

#### Step 3: Check Working Directory

```bash
# Get working directory from config
grep CLAUDE_WORKING_DIRECTORY /etc/claude-backend/.env

# Verify it exists
ls -la /path/to/working/directory

# If missing, create it
mkdir -p /path/to/working/directory
chmod 755 /path/to/working/directory
```

#### Step 4: Restart Backend

```bash
# Apply configuration changes
systemctl restart claude-backend

# Monitor logs while restarting
tail -f /var/log/claude-backend/app.log | grep -E "Claude|process|PID"

# Should see:
# "Starting Claude Code process"
# "✅ Claude Code process started successfully - PID: XXXXX"
```

---

### Troubleshooting: High Latency

**Problem**: Messages taking >30 seconds to respond  
**Time to Resolve**: 5-15 minutes

#### Step 1: Check System Resources

```bash
# CPU usage
top -b -n 1 | head -10

# Memory usage
free -h

# Disk I/O
iostat -x 1 5

# Network
netstat -an | grep ESTABLISHED | wc -l
```

**Targets**:
- ✅ CPU: < 80% (plenty of headroom)
- ✅ Memory: > 20% free
- ✅ Disk I/O: < 80% utilized
- ✅ Connections: < max connections

#### Step 2: Check Claude Process

```bash
# Is Claude process running?
ps aux | grep claude | grep -v grep

# Check Claude CPU/Memory
ps aux | grep claude | awk '{print $3, $4, $11}' # CPU%, MEM%, Command

# Check if process stuck
pstree -p | grep claude
```

**If Claude using high CPU**:
- Command is slow (expected for complex commands)
- Check what command was sent
- Verify it's a legitimate long operation

#### Step 3: Enable SQL Logging

```bash
# Check if database queries are slow
echo "SQLALCHEMY_LOG_LEVEL=INFO" >> /etc/claude-backend/.env
systemctl restart claude-backend

# Look for slow queries
grep "SELECT\|INSERT" /var/log/claude-backend/app.log | head -10

# Measure query time
grep "SELECT" /var/log/claude-backend/app.log | \
  awk '{print $1, $2, $13}' | tail -5
```

**If queries > 1 second**:
- Add database indexes
- Check database load: `SHOW PROCESSLIST;`
- Consider query optimization

#### Step 4: Check Network Latency

```bash
# Ping Claude server (if remote)
ping -c 4 claude-server

# Check WebSocket latency
# (in backend logs, look for ping/pong timing)
grep "Heartbeat\|ping" /var/log/claude-backend/app.log | tail -5
```

#### Step 5: Scale Resources (If Needed)

```bash
# If CPU/Memory saturated:

# Option 1: Restart backend to clear cache
systemctl restart claude-backend

# Option 2: Increase resources
# Edit docker-compose.yml or systemd service file
# Increase memory limit, CPU allocation
# Then restart

# Option 3: Load balance
# If multiple backends available, distribute traffic
```

---

### Troubleshooting: Disk Space

**Problem**: `/var/log` partition filling up  
**Time to Resolve**: 2-3 minutes

#### Step 1: Check Log Size

```bash
# Size of log directory
du -sh /var/log/claude-backend/

# Size of main log file
ls -lh /var/log/claude-backend/app.log

# Breakdown by file
ls -lh /var/log/claude-backend/app.log*
```

**Expected Rotation**:
- app.log: 0-3MB (current)
- app.log.1: 3MB (previous)
- app.log.2: 3MB
- app.log.3: 3MB
- Total: ~12MB max

#### Step 2: Verify Rotation Working

```bash
# Check rotation configuration
grep -A 5 "RotatingFileHandler" /etc/claude-backend/app-config.py

# Check timestamps on rotated files
ls -la /var/log/claude-backend/app.log*

# Recent file should be "now"
stat /var/log/claude-backend/app.log | grep Modify
```

**If not rotating**:
- Check maxBytes (should be 3MB)
- Check backupCount (should be 3)
- Restart backend to apply config

#### Step 3: Archive Old Logs

```bash
# Create archive
tar czf /backup/logs/claude-backend-$(date +%Y%m%d).tar.gz \
  /var/log/claude-backend/app.log.*

# Remove old backups (keep 3 rotations)
rm /var/log/claude-backend/app.log.4
rm /var/log/claude-backend/app.log.5

# Verify
ls -lh /var/log/claude-backend/
```

#### Step 4: Set Up Monitoring

```bash
# Alert if log size exceeds 2GB
cat > /etc/monitors/check-log-size.sh << 'EOF'
#!/bin/bash
LOG_DIR="/var/log/claude-backend"
THRESHOLD=2147483648  # 2GB in bytes

SIZE=$(du -s "$LOG_DIR" | awk '{print $1 * 1024}')

if [ $SIZE -gt $THRESHOLD ]; then
  echo "ALERT: Log directory exceeds 2GB"
  # Send alert
  # notify-admin "Log archive needed"
fi
EOF

chmod +x /etc/monitors/check-log-size.sh

# Run hourly via cron
echo "0 * * * * /etc/monitors/check-log-size.sh" | crontab -
```

---

## Performance Debugging

### Enable SQL Logging Temporarily

```bash
# Step 1: Update configuration
echo "SQLALCHEMY_LOG_LEVEL=INFO" >> /etc/claude-backend/.env

# Step 2: Restart backend
systemctl restart claude-backend

# Step 3: Run test command through UI
# (User sends message via frontend)

# Step 4: Analyze SQL logs
grep "SELECT\|INSERT\|UPDATE" /var/log/claude-backend/app.log | head -20

# Step 5: Disable SQL logging
sed -i 's/SQLALCHEMY_LOG_LEVEL=INFO/SQLALCHEMY_LOG_LEVEL=WARNING/' \
  /etc/claude-backend/.env
systemctl restart claude-backend
```

### Find Slow Queries

```bash
# Enable SQL logging (see above)

# Extract query timing
grep "SELECT" /var/log/claude-backend/app.log | \
  awk -F'[()]' '{
    time=$NF
    gsub(/[^0-9.]/, "", time)
    if (time > 1.0) print $0
  }'

# Result shows queries taking >1 second
```

### Profile Message Processing

```bash
# Enable debug logging
echo "LOG_LEVEL=DEBUG" >> /etc/claude-backend/.env
systemctl restart claude-backend

# Send test message
# (User sends via frontend)

# Analyze timeline
grep "Session: <session-id>" /var/log/claude-backend/app.log | \
  awk '{print $1, $2, $NF}' | \
  while read time marker msg; do
    echo "$time: $msg"
  done
```

---

## Log Tracing

### Trace Single User Message

```bash
# Get session ID from frontend or database
SESSION_ID="abc-123-def-456"

# Trace complete message flow
grep "$SESSION_ID" /var/log/claude-backend/app.log | awk '
{
  time=$1 " " $2
  if ($0 ~ /connection request/) {
    print time ": 1. Connection requested"
  } else if ($0 ~ /connection accepted/) {
    print time ": 2. Connection accepted"
  } else if ($0 ~ /Command received/) {
    print time ": 3. Command received"
  } else if ($0 ~ /Command sent to Claude/) {
    print time ": 4. Command sent"
  } else if ($0 ~ /Output chunk/) {
    print time ": 5. Output chunk received"
  } else if ($0 ~ /Command execution complete/) {
    print time ": 6. Execution complete - " $0
  } else if ($0 ~ /disconnected/) {
    print time ": 7. Disconnected"
  } else if ($0 ~ /error|ERROR/) {
    print time ": ❌ ERROR - " $0
  }
}'
```

### Trace Errors

```bash
# Find all errors in last 100 lines
tail -100 /var/log/claude-backend/app.log | grep -E "❌|ERROR|Traceback"

# Get full error with context
grep -B 3 -A 10 "❌ Command execution failed" /var/log/claude-backend/app.log

# Get stack trace
grep "Traceback\|File\|Error:" /var/log/claude-backend/app.log | tail -30
```

---

## Log Management

### Manual Rotation

```bash
# Stop backend (if needed for clean rotation)
systemctl stop claude-backend

# Rotate logs manually
mv /var/log/claude-backend/app.log /var/log/claude-backend/app.log.backup
touch /var/log/claude-backend/app.log

# Restart backend
systemctl start claude-backend
```

### Archive Strategy

```bash
# Daily archive (run via cron at midnight)
0 0 * * * tar czf /backup/logs/claude-backend-$(date +\%Y\%m\%d).tar.gz \
  /var/log/claude-backend/app.log.* && \
  rm /var/log/claude-backend/app.log.[2-9]*

# Keep 30 days of archives
find /backup/logs -name "claude-backend-*.tar.gz" -mtime +30 -delete

# Verify archives
ls -lh /backup/logs/ | tail -10
```

### Restore from Archive

```bash
# If you need logs from specific date
tar xzf /backup/logs/claude-backend-20251024.tar.gz -C /tmp/

# View archived logs
zcat /backup/logs/claude-backend-20251024.tar.gz | grep "Session: xyz"
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

```bash
# 1. Error Rate
ERROR_COUNT=$(grep -c "❌\|ERROR" /var/log/claude-backend/app.log)
echo "Errors per hour: $ERROR_COUNT"

# 2. Average Response Time
grep "Command execution complete" /var/log/claude-backend/app.log | \
  grep -oP 'Time: \K\d+' | \
  awk '{sum+=$1; count++} END {print "Avg: " sum/count "ms"}'

# 3. Availability
UPTIME=$(systemctl show claude-backend -p ActiveEnterTimestampMonotonic | \
  awk -F= '{print $2}')
echo "Backend uptime: $UPTIME seconds"

# 4. Concurrency
ACTIVE_SESSIONS=$(grep -o "Session: [^ ]*" /var/log/claude-backend/app.log | \
  sort -u | wc -l)
echo "Unique sessions today: $ACTIVE_SESSIONS"
```

### Alert Conditions

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Error rate | > 10/hour | Page on-call |
| Response time | > 60s avg | Investigate performance |
| Backend down | > 5min | Auto-restart + alert |
| Disk full | > 90% | Archive logs + alert |
| Memory usage | > 85% | Alert + check leaks |

---

## Maintenance Tasks

### Weekly

- [ ] Review error logs for patterns
- [ ] Check disk usage trend
- [ ] Verify backups completed
- [ ] Test log rotation working

### Monthly

- [ ] Review slow query logs
- [ ] Analyze performance trends
- [ ] Update runbook if needed
- [ ] Test log recovery procedure

### Quarterly

- [ ] Capacity planning (growth rate)
- [ ] Review logging configuration
- [ ] Optimize slow queries found
- [ ] Update documentation

---

## Emergency Procedures

### Backend Down

```bash
# 1. Check status
systemctl status claude-backend

# 2. Check logs for reason
tail -50 /var/log/claude-backend/app.log | grep -i error

# 3. Try restart
systemctl restart claude-backend

# 4. If still fails, check:
# - Disk space: df -h
# - Database: mysql -u user -p -h host -e "SELECT 1"
# - Ports: netstat -an | grep 8000
# - Configuration: cat /etc/claude-backend/.env

# 5. If database issue:
systemctl restart mysql
systemctl restart claude-backend

# 6. If resource issue:
# Kill other processes or scale up
```

### Database Connection Lost

```bash
# 1. Verify database is running
mysql -u user -p -h host -e "SELECT 1" || echo "DB down"

# 2. Check network connectivity
ping database-host

# 3. Check connection pool
grep -i "connection\|pool" /var/log/claude-backend/app.log | tail -10

# 4. Restart backend to reset connection pool
systemctl restart claude-backend

# 5. Monitor recovery
tail -f /var/log/claude-backend/app.log | grep -i "connect\|success"
```

### Claude Process Hanging

```bash
# 1. Identify hanging process
ps aux | grep claude | grep -v grep

# 2. Kill stuck process
pkill -9 claude

# 3. Check backend logs for what happened
tail -50 /var/log/claude-backend/app.log | grep -E "Claude|error"

# 4. Restart backend
systemctl restart claude-backend

# 5. Notify users of interruption
# (next request will reconnect)
```

---

## References

- [LOGGING_GUIDE.md](./LOGGING_GUIDE.md) - Configuration details
- [LOGGING_REFERENCE.md](./LOGGING_REFERENCE.md) - All logging points
- [CLAUDE_PROCESS_LIFECYCLE.md](./CLAUDE_PROCESS_LIFECYCLE.md) - Process debugging

---

**Last Updated**: 2025-10-25  
**Maintained By**: Infrastructure Team  
**Review Schedule**: Quarterly

