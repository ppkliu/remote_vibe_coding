# Testing Quickstart: Logging Feature

**Feature**: 002-claude-code WebSocket/Claude Code Communication Logging  
**For**: Developers running and interpreting tests  
**Test Coverage**: 60+ tests across 3 user stories

---

## TL;DR - Run Tests Now

```bash
cd backend

# Run all logging feature tests (fastest)
PYTHONPATH=. python3.12 -m pytest tests/unit/test_logging_level_toggle.py tests/unit/test_sqlalchemy_echo.py tests/integration/test_console_output.py tests/integration/test_websocket_lifecycle.py tests/integration/test_e2e_claude_communication.py -v

# Run with coverage
PYTHONPATH=. python3.12 -m pytest tests/ --cov=src --cov-report=term-missing

# Run specific user story tests (see sections below)
```

**Expected Result**: 60+ tests passing, ~85% coverage

---

## Quick Navigation

1. [Test Organization](#test-organization)
2. [Running Tests](#running-tests)
3. [Test Output Interpretation](#test-output-interpretation)
4. [Debugging Failed Tests](#debugging-failed-tests)
5. [User Story Test Suites](#user-story-test-suites)
6. [CI/CD Integration](#cicd-integration)

---

## Test Organization

### By Type

```
backend/tests/
├── unit/                                    # 16 tests (fast, isolated)
│   ├── test_logging_level_toggle.py         # 8 tests - SQLAlchemy log level config
│   └── test_sqlalchemy_echo.py              # 8 tests - echo=False verification
│
├── integration/                              # 30+ tests (with dependencies)
│   ├── test_console_output.py               # 6 tests - console cleanliness
│   ├── test_websocket_lifecycle.py          # 5 tests - connection lifecycle
│   ├── test_e2e_claude_communication.py     # 19 tests - message flow E2E
│   └── MESSAGE_FLOW_GUIDE.md                # Non-technical message flow guide
│
└── conftest.py                               # Shared fixtures
```

### By User Story

| User Story | Tests | Duration | Files |
|------------|-------|----------|-------|
| US-1: Message Response | 19 tests | ~5s | `test_e2e_claude_communication.py` |
| US-2: Process Lifecycle | 5 tests | ~1s | `test_websocket_lifecycle.py` |
| US-3: Console Cleanliness | 22 tests | ~2s | `test_console_output.py`, `test_logging_level_toggle.py`, `test_sqlalchemy_echo.py` |

---

## Running Tests

### Prerequisite Check

```bash
# Verify Python version (need 3.11+)
python3.12 --version

# Install test dependencies
python3.12 -m pip install pytest pytest-asyncio pytest-cov

# Verify PostgreSQL running (for E2E tests)
docker-compose ps postgres

# Should show: State: Up
```

### Run All Tests

```bash
cd backend

# All tests with verbose output
PYTHONPATH=. python3.12 -m pytest tests/ -v

# Parallel execution (faster)
PYTHONPATH=. python3.12 -m pytest tests/ -v -n auto

# With coverage report
PYTHONPATH=. python3.12 -m pytest tests/ --cov=src --cov-report=html
# Open: htmlcov/index.html
```

**Expected Output**:
```
tests/unit/test_logging_level_toggle.py::TestSQLAlchemyLoggingLevelToggle::test_sqlalchemy_warning_suppresses_sql PASSED [ 1%]
tests/unit/test_logging_level_toggle.py::TestSQLAlchemyLoggingLevelToggle::test_sqlalchemy_info_shows_sql PASSED [ 2%]
...
============================================ 60 passed in 8.45s ============================================
```

### Run by User Story

#### User Story 1: Message Response Visibility

```bash
# All US-1 tests (19 tests, ~5 seconds)
PYTHONPATH=. python3.12 -m pytest tests/integration/test_e2e_claude_communication.py -v

# Specific test class
PYTHONPATH=. python3.12 -m pytest tests/integration/test_e2e_claude_communication.py::TestClaudeCommunicationLogging -v

# Single test
PYTHONPATH=. python3.12 -m pytest tests/integration/test_e2e_claude_communication.py::TestClaudeCommunicationLogging::test_connection_lifecycle_logging -v
```

**What these tests verify**:
- ✅ WebSocket connection logged with session/user IDs
- ✅ Command received logged with command preview
- ✅ Command sent to Claude logged
- ✅ Output chunks logged (DEBUG level)
- ✅ Command completion logged with timing
- ✅ Disconnection logged

#### User Story 2: Process Lifecycle Logging

```bash
# All US-2 tests (5 tests, ~1 second)
PYTHONPATH=. python3.12 -m pytest tests/integration/test_websocket_lifecycle.py -v

# Specific lifecycle phase
PYTHONPATH=. python3.12 -m pytest tests/integration/test_websocket_lifecycle.py::TestWebSocketConnectionLifecycle::test_connection_acceptance_logging -v
```

**What these tests verify**:
- ✅ Connection request logged
- ✅ Connection acceptance logged with user context
- ✅ Message reception logged
- ✅ Disconnection logged
- ✅ Context propagation (session_id in all logs)

#### User Story 3: Console Cleanliness

```bash
# All US-3 tests (22 tests, ~2 seconds)
PYTHONPATH=. python3.12 -m pytest tests/unit/test_logging_level_toggle.py tests/unit/test_sqlalchemy_echo.py tests/integration/test_console_output.py -v

# Just SQL suppression tests
PYTHONPATH=. python3.12 -m pytest tests/unit/test_sqlalchemy_echo.py -v

# Just console output tests
PYTHONPATH=. python3.12 -m pytest tests/integration/test_console_output.py -v

# Just log level toggle tests
PYTHONPATH=. python3.12 -m pytest tests/unit/test_logging_level_toggle.py -v
```

**What these tests verify**:
- ✅ No SQL statements on console (SELECT, INSERT, UPDATE, DELETE)
- ✅ Application logs visible on console (✅ ❌ 📨 📦 🔨 🔌)
- ✅ SQLAlchemy echo=False hardcoded
- ✅ SQLALCHEMY_LOG_LEVEL configurable via .env
- ✅ Console output concise (<100 lines typical)

### Run with Filters

```bash
# Only tests matching "sql"
PYTHONPATH=. python3.12 -m pytest tests/ -k sql -v

# Only tests matching "console"
PYTHONPATH=. python3.12 -m pytest tests/ -k console -v

# Only tests matching "lifecycle"
PYTHONPATH=. python3.12 -m pytest tests/ -k lifecycle -v

# Skip E2E tests (if Claude not installed)
PYTHONPATH=. python3.12 -m pytest tests/ -v -m "not e2e"
```

---

## Test Output Interpretation

### Successful Test Run

```
tests/integration/test_console_output.py::TestConsoleOutputCleanliness::test_console_has_no_sql_logs PASSED [ 85%]
tests/integration/test_console_output.py::TestConsoleOutputCleanliness::test_console_has_application_logs PASSED [ 90%]
tests/integration/test_console_output.py::TestConsoleOutputCleanliness::test_emoji_indicators_visibility PASSED [ 95%]

============================================ 60 passed in 8.45s ============================================
```

**Interpretation**:
- ✅ All 60 tests passed
- ✅ Feature is working correctly
- ✅ Ready for deployment

### Failed Test Example

```
FAILED tests/unit/test_sqlalchemy_echo.py::TestSQLAlchemyEchoDisabled::test_sqlalchemy_echo_disabled_in_dependencies
AssertionError: assert False
```

**What to check**:
1. **Read failure details**: pytest shows assertion that failed
2. **Check logs**: `tail -50 logs/app.log`
3. **Verify configuration**: `grep SQLALCHEMY backend/.env`
4. **Check dependencies**: Engine created correctly?

### Skipped Tests

```
tests/integration/test_e2e_claude_communication.py::TestClaudeCommunicationE2E::test_real_claude_command SKIPPED [100%]
Reason: Claude Code not installed
```

**Interpretation**:
- ⚠️ Test requires Claude Code executable
- ✅ Normal in CI/CD environments
- ℹ️ Install Claude Code to run these tests locally

---

## Debugging Failed Tests

### Step 1: Identify the Test

```bash
# Run single failing test with verbose output
PYTHONPATH=. python3.12 -m pytest tests/unit/test_sqlalchemy_echo.py::TestSQLAlchemyEchoDisabled::test_sqlalchemy_echo_disabled_in_dependencies -vv
```

**Look for**:
- Assertion error details
- Expected vs actual values
- Stack trace location

### Step 2: Enable Debug Logging

```python
# Add to test file temporarily
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or run with pytest logging:
```bash
PYTHONPATH=. python3.12 -m pytest tests/unit/test_sqlalchemy_echo.py -vv --log-cli-level=DEBUG
```

### Step 3: Check Configuration

```bash
# Verify .env file
cat backend/.env | grep -E "LOG|SQL"

# Should show:
# LOG_DIR=logs
# LOG_LEVEL=INFO
# SQLALCHEMY_LOG_LEVEL=WARNING

# Check logs directory
ls -la backend/logs/

# Check recent logs
tail -50 backend/logs/app.log
```

### Step 4: Check Dependencies

```bash
# Verify database
docker-compose ps postgres

# Verify Python packages
python3.12 -m pip list | grep -E "pytest|sqlalchemy|fastapi"

# Restart database if needed
docker-compose restart postgres
```

### Step 5: Run in Isolation

```bash
# Drop database and recreate (if needed)
docker-compose down postgres
docker-compose up -d postgres

# Wait 5 seconds for startup
sleep 5

# Re-run migrations
PYTHONPATH=. python3.12 -m alembic upgrade head

# Re-run test
PYTHONPATH=. python3.12 -m pytest tests/unit/test_sqlalchemy_echo.py -v
```

### Common Issues

#### Issue: "ModuleNotFoundError: No module named 'src'"

**Fix**: Use `PYTHONPATH=.` prefix:
```bash
PYTHONPATH=. python3.12 -m pytest tests/ -v
```

#### Issue: "Database connection failed"

**Fix**: Start PostgreSQL:
```bash
docker-compose up -d postgres
sleep 5
PYTHONPATH=. python3.12 -m pytest tests/ -v
```

#### Issue: "Fixture 'db_session' not found"

**Fix**: Verify `conftest.py` exists:
```bash
ls backend/tests/conftest.py
# Should exist

# Re-run with --collect-only to see fixtures
PYTHONPATH=. python3.12 -m pytest tests/ --collect-only
```

#### Issue: "SQL queries appearing on console during tests"

**Check**:
```bash
# 1. Verify SQLALCHEMY_LOG_LEVEL
grep SQLALCHEMY_LOG_LEVEL backend/.env

# 2. Should be WARNING, not INFO/DEBUG
# If wrong, fix:
echo "SQLALCHEMY_LOG_LEVEL=WARNING" >> backend/.env

# 3. Re-run tests
PYTHONPATH=. python3.12 -m pytest tests/integration/test_console_output.py -v
```

---

## User Story Test Suites

### US-1: Message Response Visibility (SC-001, SC-002)

**File**: `tests/integration/test_e2e_claude_communication.py`  
**Tests**: 19 tests  
**Duration**: ~5 seconds  
**Database Required**: Yes  
**Claude Required**: No (uses mocks)

#### Success Criteria

**SC-001**: Every WebSocket message visible in logs
- ✅ test_connection_lifecycle_logging
- ✅ test_command_received_logging
- ✅ test_command_sent_to_claude_logging
- ✅ test_output_streaming_logging

**SC-002**: Logs include session_id, user_id, command, timestamp
- ✅ test_logs_include_session_id
- ✅ test_logs_include_user_id
- ✅ test_logs_include_command_preview
- ✅ test_logs_include_timestamps

#### Run US-1 Tests

```bash
# All US-1 tests
PYTHONPATH=. python3.12 -m pytest tests/integration/test_e2e_claude_communication.py -v

# Just success criteria SC-001
PYTHONPATH=. python3.12 -m pytest tests/integration/test_e2e_claude_communication.py -k "lifecycle or command_received or command_sent or output_streaming" -v

# Just success criteria SC-002
PYTHONPATH=. python3.12 -m pytest tests/integration/test_e2e_claude_communication.py -k "session_id or user_id or command or timestamp" -v
```

#### Expected Output

```
test_connection_lifecycle_logging PASSED
test_command_received_logging PASSED
test_command_sent_to_claude_logging PASSED
test_output_streaming_logging PASSED
test_logs_include_session_id PASSED
test_logs_include_user_id PASSED
test_logs_include_command_preview PASSED
test_logs_include_timestamps PASSED
...
============================================ 19 passed in 5.23s ============================================
```

### US-2: Process Lifecycle Logging (SC-004, SC-005)

**File**: `tests/integration/test_websocket_lifecycle.py`  
**Tests**: 5 tests  
**Duration**: ~1 second  
**Database Required**: No  
**Claude Required**: No

#### Success Criteria

**SC-004**: Process start/stop logged with PID
- ✅ test_connection_request_logging
- ✅ test_connection_acceptance_logging

**SC-005**: Errors logged with context
- ✅ test_message_reception_logging
- ✅ test_disconnection_logging
- ✅ test_context_propagation

#### Run US-2 Tests

```bash
# All US-2 tests
PYTHONPATH=. python3.12 -m pytest tests/integration/test_websocket_lifecycle.py -v

# Just success criteria SC-004
PYTHONPATH=. python3.12 -m pytest tests/integration/test_websocket_lifecycle.py::TestWebSocketConnectionLifecycle::test_connection_acceptance_logging -v

# Just success criteria SC-005
PYTHONPATH=. python3.12 -m pytest tests/integration/test_websocket_lifecycle.py::TestWebSocketConnectionLifecycle::test_context_propagation -v
```

#### Expected Output

```
test_connection_request_logging PASSED
test_connection_acceptance_logging PASSED
test_message_reception_logging PASSED
test_disconnection_logging PASSED
test_context_propagation PASSED
============================================ 5 passed in 1.12s ============================================
```

### US-3: Console Cleanliness (SC-003)

**Files**: 
- `tests/unit/test_logging_level_toggle.py` (8 tests)
- `tests/unit/test_sqlalchemy_echo.py` (8 tests)
- `tests/integration/test_console_output.py` (6 tests)

**Tests**: 22 tests  
**Duration**: ~2 seconds  
**Database Required**: No  
**Claude Required**: No

#### Success Criteria

**SC-003**: SQL logs suppressed by default
- ✅ test_sqlalchemy_echo_disabled_in_dependencies
- ✅ test_sqlalchemy_warning_suppresses_sql
- ✅ test_console_has_no_sql_logs

**FR-012**: Toggleable via environment variable
- ✅ test_sqlalchemy_level_configurable_via_env
- ✅ test_no_code_changes_needed_to_toggle
- ✅ test_sqlalchemy_info_shows_sql
- ✅ test_sqlalchemy_debug_shows_detailed_sql

#### Run US-3 Tests

```bash
# All US-3 tests
PYTHONPATH=. python3.12 -m pytest tests/unit/test_logging_level_toggle.py tests/unit/test_sqlalchemy_echo.py tests/integration/test_console_output.py -v

# Just SC-003 (SQL suppression)
PYTHONPATH=. python3.12 -m pytest tests/ -k "echo or suppresses_sql or no_sql" -v

# Just FR-012 (toggleable)
PYTHONPATH=. python3.12 -m pytest tests/unit/test_logging_level_toggle.py -k "configurable or toggle or info_shows or debug_shows" -v

# Just console cleanliness
PYTHONPATH=. python3.12 -m pytest tests/integration/test_console_output.py -v
```

#### Expected Output

```
test_sqlalchemy_echo_disabled_in_dependencies PASSED
test_sqlalchemy_warning_suppresses_sql PASSED
test_console_has_no_sql_logs PASSED
test_sqlalchemy_level_configurable_via_env PASSED
test_no_code_changes_needed_to_toggle PASSED
test_sqlalchemy_info_shows_sql PASSED
test_sqlalchemy_debug_shows_detailed_sql PASSED
...
============================================ 22 passed in 2.34s ============================================
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test-logging.yml
name: Test Logging Feature

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: admin
          POSTGRES_DB: claude_remote
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          PYTHONPATH=. python3.12 -m pytest tests/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "Running logging feature tests..."
cd backend
PYTHONPATH=. python3.12 -m pytest tests/unit/test_logging_level_toggle.py tests/unit/test_sqlalchemy_echo.py -v

if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Commit aborted."
    exit 1
fi

echo "✅ Tests passed!"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Performance Benchmarks

Typical test durations on standard hardware:

| Test Suite | Tests | Duration | Notes |
|------------|-------|----------|-------|
| Unit tests (all) | 16 | ~2s | No database needed |
| Integration tests (all) | 30+ | ~8s | Requires PostgreSQL |
| **Total** | **60+** | **~10s** | Fast feedback loop |

**Coverage**: ~85% of logging-related code

---

## Next Steps After Tests Pass

1. ✅ Verify all 60+ tests passing
2. ✅ Check coverage report (should be 80%+)
3. ✅ Review log files generated during tests: `backend/logs/app.log`
4. ✅ Test manually with real WebSocket connection (see LOGGING_GUIDE.md)
5. ✅ Deploy to staging environment
6. ✅ Monitor logs in production

---

## Related Documentation

- **[LOGGING_GUIDE.md](../LOGGING_GUIDE.md)** - Operator configuration guide
- **[LOGGING_REFERENCE.md](../LOGGING_REFERENCE.md)** - Complete logging points catalog
- **[MESSAGE_FLOW_GUIDE.md](./integration/MESSAGE_FLOW_GUIDE.md)** - Message flow tracing
- **[CLAUDE_PROCESS_LIFECYCLE.md](../CLAUDE_PROCESS_LIFECYCLE.md)** - Process debugging

---

## Questions?

**Test failures?** See [Debugging Failed Tests](#debugging-failed-tests)  
**Setup issues?** Verify [Prerequisite Check](#prerequisite-check)  
**CI/CD integration?** See [CI/CD Integration](#cicd-integration)

**End of Testing Quickstart**
