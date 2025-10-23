# Tasks: Debug and Fix WebSocket/Claude Code Communication

**Feature**: Debug and Fix WebSocket/Claude Code Communication
**Branch**: `002-claude-code`
**Specification**: `/specs/002-claude-code/spec.md`
**Implementation Plan**: `/specs/002-claude-code/plan.md`
**Total Tasks**: 22 tasks across 4 phases
**Estimated Duration**: 3-4 days (1-2 days testing, 1-2 days documentation)

---

## Executive Summary

This feature enables complete visibility into WebSocket-to-Claude communication through comprehensive logging and fixes the issue where users send messages but receive no response.

**Implementation Status**: 95% complete (logging already in place from previous work)
**Remaining Work**: Testing and documentation to verify implementation

**MVP Scope**: Complete User Story 1 (User sends message and receives Claude response)
**Full Scope**: All 3 user stories + documentation

---

## Dependency Graph & Execution Strategy

### User Story Completion Order

```
Phase 2 (Foundational)
    └─→ Phase 3 (US1: P1 - Message Response)
            └─→ Phase 4 (US2: P1 - Process Lifecycle)
                    └─→ Phase 5 (US3: P2 - Console Cleanliness)
                            └─→ Phase 6 (Polish & Documentation)
```

**Independent Delivery**: Each user story can be completed and deployed independently:
- **US1 alone**: Users can send messages and see responses with logging
- **US1 + US2**: Full debugging visibility into Claude process
- **US1 + US2 + US3**: Clean, professional logging output

### Parallelization Opportunities

**Within User Story 1**:
- [P] Test contract generation (test files creation) - can start immediately
- [P] WebSocket handler testing - can run parallel with Claude bridge testing
- [P] Integration test setup - can prepare fixtures while writing specific tests

**Within User Story 2**:
- [P] Process lifecycle logging verification - independent of message logging
- [P] Error path testing - independent of success path testing

**Within User Story 3**:
- [P] SQLAlchemy echo verification - independent of console output verification
- [P] Logging configuration testing - independent of integration testing

---

## Phase 1: Setup & Project Initialization

*No setup needed - all infrastructure in place from previous work*

---

## Phase 2: Foundational Prerequisites

*Foundational tasks that must complete before any user story implementation*

### T001: Verify existing logging infrastructure (1 hour) ✅

**Objective**: Confirm all logging components are properly configured and working

**Description**:
- Review `backend/src/logging_config.py` - verify RotatingFileHandler configuration
- Check `backend/src/main.py` - verify logging initialization at startup
- Confirm `.env` has all required logging configuration parameters:
  - `LOG_DIR=logs`
  - `LOG_LEVEL=INFO`
  - `SQLALCHEMY_LOG_LEVEL=WARNING`
  - `CLAUDE_WORKING_DIRECTORY=.`
- Start backend and verify startup logs appear (with configuration shown)
- Verify logs directory created with proper permissions

**Acceptance Criteria**:
- ✅ Startup logs show configuration (Server, Debug, Claude Code path, Working Directory, Log Directory, SQLAlchemy Level)
- ✅ Logs directory exists with write permissions
- ✅ No errors during startup logging initialization
- ✅ .env file contains all required parameters

**Files Affected**:
- `backend/src/logging_config.py` (read-only verification)
- `backend/src/main.py` (read-only verification)
- `backend/.env` (verify, don't modify)

**Verification Command**:
```bash
cd backend && python3.12 -c "from src.logging_config import setup_logging; logger = setup_logging(); print('✅ Logging infrastructure initialized')"
```

---

### T002: Review all logging points in existing code (1 hour) ✅

**Objective**: Create inventory of existing logging for reference during testing

**Description**:
- Review `backend/src/api/websocket.py` (48 logging lines) - document all logging points:
  - Connection acceptance logging
  - Message reception logging
  - Command sending logging
  - Output chunk logging
  - Error handling logging
  - Disconnection logging
- Review `backend/src/services/claude_bridge.py` - document process logging:
  - Process startup logging
  - Command sending logging
  - Output reading logging
  - Error logging
- Review `backend/src/services/session_manager.py` - document session logging:
  - Process startup logging
  - Session management logging
- Create summary table of all logging points with logger names and levels

**Acceptance Criteria**:
- ✅ All logging points documented in summary table
- ✅ Table includes file, function, level (INFO/DEBUG), and purpose
- ✅ Verified 20+ logging points exist
- ✅ Summary saved for test reference

**Files Affected**:
- `backend/src/api/websocket.py` (review)
- `backend/src/services/claude_bridge.py` (review)
- `backend/src/services/session_manager.py` (review)

---

### T003: Verify SQLAlchemy logging suppression (30 min) ✅

**Objective**: Confirm SQLAlchemy logs are suppressed from console (US3 foundation)

**Description**:
- Verify `backend/src/api/dependencies.py` has `echo=False` (not `echo=settings.DEBUG`)
- Verify `backend/src/logging_config.py` sets `sqlalchemy.engine` logger to `WARNING` level
- Start backend and run a simple test command (login, send message)
- Check console output - should show NO "sqlalchemy.engine.Engine SELECT/INSERT" lines
- Check log file - should contain complete SQL queries if needed for debugging
- Verify environment variable `SQLALCHEMY_LOG_LEVEL=WARNING` is respected

**Acceptance Criteria**:
- ✅ No SQL logs appear on console
- ✅ `dependencies.py` has `echo=False`
- ✅ `logging_config.py` sets sqlalchemy logger to WARNING
- ✅ Log file still contains SQL (for offline debugging)
- ✅ Setting `SQLALCHEMY_LOG_LEVEL=INFO` temporarily shows SQL logs

**Files Affected**:
- `backend/src/api/dependencies.py` (verify)
- `backend/src/logging_config.py` (verify)
- `backend/.env` (verify)

---

## Phase 3: User Story 1 - User Sends Message and Receives Claude Response (P1)

**Story Goal**: Users can send messages through the chat interface and receive Claude Code responses with visible logging showing progress

**Independent Test**: Send message "hello" → see Claude process start within 5s → see command sent within 10s → receive output within 30s

**Story Acceptance Criteria**:
- ✅ Backend logs show "Claude process started" within 5 seconds of WebSocket connection
- ✅ Backend logs show "Command sent to Claude" within 10 seconds
- ✅ User receives output chunks within 30 seconds
- ✅ Error messages are clear and include full stack traces
- ✅ All user-facing error scenarios are handled

**Deliverables**: Integration tests, documentation of message flow

---

### T004: Create test fixtures for WebSocket testing [P] (1 hour) ✅

**Objective**: Set up reusable test infrastructure for all WebSocket tests

**Description**:
- Create `backend/tests/conftest.py` with pytest fixtures for:
  - Logged-in user (with authentication token)
  - WebSocket connection mock/client
  - Caplog fixture configuration for log assertions
  - Database session for test cleanup
- Create test data factory for creating test users, sessions, messages
- Set up mock Claude process for testing without actual Claude Code
- Configure test logging to use MemoryHandler for assertion

**Acceptance Criteria**:
- ✅ Fixtures can create authenticated user with valid token
- ✅ Fixtures can establish WebSocket connection in tests
- ✅ Can capture and assert on log output in tests
- ✅ Can mock Claude process responses
- ✅ Test cleanup properly removes test data

**Files Created**:
- `backend/tests/conftest.py` (fixtures and configuration)
- `backend/tests/factories.py` (test data factories)

**Dependencies**: None (foundational infrastructure)

---

### T005: Write integration test for complete message flow [P] (2 hours) ✅

**Objective**: Test the complete message lifecycle with log assertions

**Test File**: `backend/tests/integration/test_websocket_logging.py`

**Description**:
- Test scenario: User sends "hello" command
- Assertions on log output:
  - ✅ "WebSocket connection accepted" appears within first 5 log entries
  - ✅ "Claude process started" appears within 5 seconds (check timestamp)
  - ✅ "Command sent to Claude" appears within 10 seconds
  - ✅ "Output chunk" logs appear with sequence numbers
  - ✅ "Command execution complete" appears with execution time
- Verify log format includes required context:
  - Session ID appears in all relevant logs
  - User ID appears in all relevant logs
  - Connection ID appears in lifecycle logs
- Test error scenario: Invalid message → error log with stack trace

**Test Cases**:
1. `test_successful_message_flow` - Happy path with assertions on all logging points
2. `test_message_with_error` - Error path ensures stack trace is logged
3. `test_connection_lifecycle_logging` - Connection → accept → command → disconnect

**Acceptance Criteria**:
- ✅ All 3 test cases pass
- ✅ Log assertions validate log content and timing
- ✅ Session/user/connection IDs present in logs
- ✅ Test runs in <5 seconds with mocked Claude

**Files Created**:
- `backend/tests/integration/test_websocket_logging.py`

**Dependencies**: T004 (fixtures)

---

### T006: Write integration test for end-to-end message flow with real Claude [P] (1 hour) ✅

**Objective**: Test actual message processing with real Claude Code (optional, for full validation)

**Test File**: `backend/tests/integration/test_e2e_claude_communication.py`

**Description**:
- Test scenario: Send actual command to Claude Code
- Verify:
  - Claude process starts and receives command
  - Output is streamed back with proper sequence numbers
  - Frontend receives output in expected format
  - Execution time is logged accurately
- This test requires Claude Code to be installed and available
- Test can be marked `@pytest.mark.integration` to run separately
- Uses real Claude process (not mocked)

**Test Cases**:
1. `test_send_simple_command_to_claude` - e.g., `echo "hello"`
2. `test_receive_output_chunks_correctly` - Verify chunking
3. `test_execution_time_calculation` - Verify timing logged correctly

**Acceptance Criteria**:
- ✅ Test can be skipped if Claude not available (`pytest.mark.skipif`)
- ✅ All 3 test cases pass when Claude is available
- ✅ Output format matches expected structure
- ✅ Timing calculations are accurate (within 1 second)

**Files Created**:
- `backend/tests/integration/test_e2e_claude_communication.py`

**Dependencies**: T004 (fixtures), T005 (proves logging works)

**Note**: Can be skipped in CI if Claude not available - use `@pytest.mark.skipif`

---

### T007: Document message flow with screenshots (30 min) ✅

**Objective**: Create user-facing documentation of the message flow

**Description**:
- Create markdown document showing:
  - Step-by-step message flow with expected timings
  - Example backend logs for successful message
  - Example backend logs for error scenarios
  - Expected frontend output progression
- Include log excerpts showing:
  - Connection acceptance logs
  - Process startup logs
  - Command sending logs
  - Output chunk logs with sequence numbers
  - Completion logs with execution time

**Acceptance Criteria**:
- ✅ Documentation is clear for non-technical users
- ✅ Includes real log examples
- ✅ Explains what each log entry means
- ✅ Explains how to interpret timing

**Files Created**:
- `backend/tests/integration/MESSAGE_FLOW_GUIDE.md`

**Dependencies**: T005 (provides real log examples)

---

### T008: Create unit test for logging configuration (1 hour) ✅

**Objective**: Verify logging configuration works as expected

**Test File**: `backend/tests/unit/test_logging_configuration.py`

**Description**:
- Test that logging levels are configurable via environment variables
- Test that SQLAlchemy logging can be toggled without code changes
- Test that emoji indicators appear in log messages
- Test that log formatting includes required fields:
  - Timestamp
  - Logger name
  - Level (INFO/DEBUG/ERROR)
  - Session ID (when applicable)
  - User ID (when applicable)
  - Message with emoji indicator

**Test Cases**:
1. `test_logging_level_configuration` - Verify INFO level set correctly
2. `test_sqlalchemy_logging_suppression` - SQLAlchemy at WARNING by default
3. `test_sqlalchemy_logging_toggle` - Can enable via SQLALCHEMY_LOG_LEVEL=INFO
4. `test_emoji_indicators_in_logs` - ✅ and ❌ appear correctly
5. `test_log_format_includes_context` - Session/user IDs in output

**Acceptance Criteria**:
- ✅ All 5 test cases pass
- ✅ Can verify logging without needing actual message flow
- ✅ Tests are independent and fast (<1 second total)

**Files Created**:
- `backend/tests/unit/test_logging_configuration.py`

**Dependencies**: None (unit tests)

---

### Checkpoint: User Story 1 Complete ✅

**At this point**:
- ✅ Message flow works with comprehensive logging
- ✅ All logging points tested and verified
- ✅ Users can see progress of their messages
- ✅ Errors are logged with full context
- ✅ **Can deploy this user story alone** - users get working chat + debugging visibility

**Verification**:
```bash
cd backend
pytest tests/integration/test_websocket_logging.py tests/unit/test_logging_configuration.py -v
```

---

## Phase 4: User Story 2 - Backend Logs Show Claude Process Lifecycle (P1)

**Story Goal**: Backend operators have complete visibility into Claude Code process startup, execution, and cleanup

**Independent Test**: Initiate chat session → check logs show: session created → process starting → process started with PID → commands sent → output read → cleanup on disconnect

**Story Acceptance Criteria**:
- ✅ Connection lifecycle fully logged (accept, command, output, disconnect)
- ✅ Process startup logged with executable path, working directory, PID
- ✅ Errors logged with actionable messages and stack traces
- ✅ Cleanup logged with resource release confirmation
- ✅ All logging points include session/user/connection context

**Deliverables**: Integration tests, process lifecycle documentation

---

### T009: Write test for WebSocket connection lifecycle logging [P] (1 hour)

**Objective**: Verify all connection lifecycle events are logged

**Test File**: `backend/tests/integration/test_websocket_lifecycle.py`

**Description**:
- Test connection establishment:
  - Verify "WebSocket connection request" appears with session ID
  - Verify "Token verified" appears
  - Verify "WebSocket connection accepted" appears with user/session context
- Test message lifecycle:
  - Verify each message appears in logs with content summary
  - Verify message type detection (command/pong/tool_approval)
- Test disconnection:
  - Verify "WebSocket disconnected" appears
  - Verify "Connection ID" in disconnect log
  - Verify "cleanup complete" appears

**Test Cases**:
1. `test_connection_acceptance_logging` - Connection → accept with IDs
2. `test_message_reception_logging` - Each message type logged
3. `test_disconnection_logging` - Disconnect and cleanup logged

**Acceptance Criteria**:
- ✅ All 3 test cases pass
- ✅ Log entries include session ID, user ID, connection ID
- ✅ Timing is accurate (connection logged immediately)
- ✅ Test can run independently of other tests

**Files Created**:
- `backend/tests/integration/test_websocket_lifecycle.py`

**Dependencies**: T004 (fixtures)

---

### T010: Write test for Claude process startup logging [P] (1.5 hours)

**Objective**: Verify process startup logging includes all required information

**Test File**: `backend/tests/integration/test_claude_process_logging.py`

**Description**:
- Test process startup success:
  - Verify "Claude executable path" appears with correct path
  - Verify "Working directory" appears with correct path
  - Verify "Claude process started successfully" appears
  - Verify "PID" appears in logs (process ID)
- Test process startup failure:
  - Mock Claude executable not found
  - Verify error logged with actionable message
  - Verify stack trace includes full error details
- Test process information:
  - Verify all process info logged before "started successfully"
  - Verify information is complete and accurate

**Test Cases**:
1. `test_process_startup_success_logging` - Happy path with all info
2. `test_process_startup_failure_logging` - Error case with stack trace
3. `test_process_info_completeness` - All required fields present

**Acceptance Criteria**:
- ✅ All 3 test cases pass
- ✅ Path and PID logged accurately
- ✅ Errors include actionable message
- ✅ Stack traces are complete (not truncated)

**Files Created**:
- `backend/tests/integration/test_claude_process_logging.py`

**Dependencies**: T004 (fixtures)

---

### T011: Write test for command and output logging [P] (1.5 hours)

**Objective**: Verify command sending and output reading are fully logged

**Test File**: `backend/tests/integration/test_message_processing_logging.py`

**Description**:
- Test command sending:
  - Verify "Sending command to Claude" appears
  - Verify command text (or first N chars) appears in logs
  - Verify "Command sent to Claude" confirmation appears
- Test output reading:
  - Verify "Starting to read Claude output" appears
  - Verify each "Output chunk" appears with sequence number
  - Verify chunk content length appears in logs
  - Verify "Command execution complete" appears
  - Verify "Chunks received" and "execution time" appear
- Test streaming:
  - Verify chunks logged in order (sequence number 1, 2, 3...)
  - Verify no gaps in sequence numbers

**Test Cases**:
1. `test_command_sending_logging` - Command → sent with content
2. `test_output_chunk_logging` - Each chunk logged with sequence
3. `test_streaming_completeness` - All chunks logged in order

**Acceptance Criteria**:
- ✅ All 3 test cases pass
- ✅ Sequences are accurate and in order
- ✅ Execution time calculated correctly
- ✅ No chunk loss or duplication in logs

**Files Created**:
- `backend/tests/integration/test_message_processing_logging.py`

**Dependencies**: T004 (fixtures), T005 (proves message flow works)

---

### T012: Write test for error scenarios logging [P] (1 hour)

**Objective**: Verify all error paths log with full context and stack traces

**Test File**: `backend/tests/integration/test_error_logging.py`

**Description**:
- Test error scenarios:
  - Claude process crash → error logged with stack trace
  - WebSocket disconnection during execution → error logged
  - Database unavailable → error logged with details
  - Invalid message → error logged with message content
  - Tool approval request error → error logged
- Verify all errors include:
  - Clear error message
  - Full stack trace
  - Session/user/connection context
  - Timestamp

**Test Cases**:
1. `test_process_crash_logging` - Process error captured with trace
2. `test_connection_drop_logging` - Disconnect during execution
3. `test_invalid_message_logging` - Malformed JSON → error
4. `test_database_error_logging` - DB operation fails → logged

**Acceptance Criteria**:
- ✅ All 4 test cases pass
- ✅ Stack traces are complete (not truncated)
- ✅ Error messages are specific and actionable
- ✅ Context information present in all error logs

**Files Created**:
- `backend/tests/integration/test_error_logging.py`

**Dependencies**: T004 (fixtures)

---

### T013: Document Claude process lifecycle (30 min)

**Objective**: Create comprehensive guide to debugging Claude communication

**Description**:
- Create markdown with:
  - Process lifecycle diagram (connection → startup → command → output → cleanup)
  - Log examples for each stage
  - What each log entry means
  - How to interpret timing
  - Common errors and what they indicate
  - How to trace a complete message flow through logs

**Files Created**:
- `backend/CLAUDE_PROCESS_LIFECYCLE.md`

**Acceptance Criteria**:
- ✅ Includes real log examples
- ✅ Explains expected timings
- ✅ Includes troubleshooting guide

**Dependencies**: T009-T012 (provides real examples)

---

### Checkpoint: User Story 2 Complete ✅

**At this point**:
- ✅ Claude process lifecycle is fully logged and tested
- ✅ All startup, execution, and cleanup events are visible
- ✅ Errors are logged with full context
- ✅ Operators can debug any communication issue
- ✅ **Can deploy this user story** - full debugging visibility added

**Verification**:
```bash
cd backend
pytest tests/integration/test_websocket_lifecycle.py \
        tests/integration/test_claude_process_logging.py \
        tests/integration/test_message_processing_logging.py \
        tests/integration/test_error_logging.py -v
```

---

## Phase 5: User Story 3 - Console Output is Clean and Readable (P2)

**Story Goal**: Backend console output shows only application-level events, not database SQL noise

**Independent Test**: Start backend with DEBUG=true, send message → console shows only WebSocket/Claude logs, zero SQL logs

**Story Acceptance Criteria**:
- ✅ No SQLAlchemy SQL logs on console (SELECT/INSERT/UPDATE/COMMIT)
- ✅ All application-level logs visible (WebSocket, Claude, Session)
- ✅ Logs can be filtered to specific components if needed
- ✅ SQL logs still available in log files for offline debugging
- ✅ Can toggle SQL logging without code changes via environment variable

**Deliverables**: Configuration tests, operator documentation

---

### T014: Write test for SQLAlchemy echo disabled (30 min)

**Objective**: Verify SQLAlchemy echo is completely disabled

**Test File**: `backend/tests/unit/test_sqlalchemy_echo.py`

**Description**:
- Verify `dependencies.py` has `echo=False` (not configurable)
- Perform database operation and capture output
- Assert no SQL appears on stdout
- Verify SQLAlchemy engine doesn't output to console

**Test Cases**:
1. `test_sqlalchemy_echo_disabled` - Echo is False in engine config
2. `test_no_sql_on_console` - Database operation → no SQL output

**Acceptance Criteria**:
- ✅ Both test cases pass
- ✅ Echo hardcoded to False (not dependent on DEBUG setting)
- ✅ No SQL appears on console with any configuration

**Files Created**:
- `backend/tests/unit/test_sqlalchemy_echo.py`

**Dependencies**: None (unit test)

---

### T015: Write test for console output filtering [P] (1 hour)

**Objective**: Verify console only shows application logs, not system logs

**Test File**: `backend/tests/integration/test_console_output.py`

**Description**:
- Capture console output while sending a message
- Verify output contains:
  - ✅ WebSocket connection logs
  - ✅ Claude process logs
  - ✅ Message processing logs
- Verify output does NOT contain:
  - ❌ "sqlalchemy.engine.Engine"
  - ❌ "SELECT", "INSERT", "UPDATE", "COMMIT" (SQL statements)
  - ❌ SQLAlchemy pool logs
- Count log lines - should be <100 for single message operation

**Test Cases**:
1. `test_console_has_no_sql_logs` - Send message → verify no SQL
2. `test_console_has_application_logs` - Send message → verify WebSocket/Claude logs present
3. `test_console_output_conciseness` - Log output under 100 lines for single message

**Acceptance Criteria**:
- ✅ All 3 test cases pass
- ✅ No SQL on console even with DEBUG=true
- ✅ Application logs clearly visible and readable
- ✅ Output is concise (not verbose)

**Files Created**:
- `backend/tests/integration/test_console_output.py`

**Dependencies**: T004 (fixtures), T014 (echo disabled)

---

### T016: Write test for logging level configuration toggle [P] (1 hour)

**Objective**: Verify SQL logging can be toggled via environment variable without code changes

**Test File**: `backend/tests/unit/test_logging_level_toggle.py`

**Description**:
- Test default behavior:
  - Set `SQLALCHEMY_LOG_LEVEL=WARNING`
  - Verify SQLAlchemy logger at WARNING level
  - Verify no SQL on console
- Test toggling to INFO:
  - Set `SQLALCHEMY_LOG_LEVEL=INFO`
  - Restart application
  - Perform database operation
  - Verify SQL appears in logs
- Test toggling back:
  - Set `SQLALCHEMY_LOG_LEVEL=WARNING`
  - Verify SQL disappears from logs
- Verify no code changes needed

**Test Cases**:
1. `test_sqlalchemy_warning_suppresses_sql` - Default behavior
2. `test_sqlalchemy_info_shows_sql` - Toggled on
3. `test_sqlalchemy_level_configurable_via_env` - No code changes needed

**Acceptance Criteria**:
- ✅ All 3 test cases pass
- ✅ Configuration via environment variable works
- ✅ No code modification needed to toggle
- ✅ Setting is read at startup

**Files Created**:
- `backend/tests/unit/test_logging_level_toggle.py`

**Dependencies**: None (unit test)

---

### T017: Create operator documentation for SQL logging (30 min)

**Objective**: Document how to enable SQL logging for debugging database issues

**Description**:
- Create markdown document with:
  - When to enable SQL logging (debugging database issues, performance analysis)
  - How to enable: Set `SQLALCHEMY_LOG_LEVEL=INFO` in `.env`
  - How to view: Check `logs/app.log` for SQL statements
  - How to disable: Set `SQLALCHEMY_LOG_LEVEL=WARNING` (default)
  - Example SQL log output
  - Troubleshooting: SQL logs not showing?
- Add to existing logging documentation

**Files Modified**:
- Update `backend/LOGGING_GUIDE.md` with SQL logging toggle instructions

**Acceptance Criteria**:
- ✅ Clear, actionable instructions
- ✅ Explains when and why to use
- ✅ Includes examples
- ✅ Troubleshooting section included

**Dependencies**: T014-T016 (testing confirms feature works)

---

### Checkpoint: User Story 3 Complete ✅

**At this point**:
- ✅ Console output is clean and focused on application events
- ✅ SQL logging can be toggled without code changes
- ✅ Operators know how to enable SQL logging when needed
- ✅ Log files preserve complete history for offline debugging
- ✅ **Can deploy this user story** - professional logging output

**Verification**:
```bash
cd backend
# Verify console is clean
pytest tests/integration/test_console_output.py -v -s
# Verify configuration works
pytest tests/unit/test_sqlalchemy_echo.py \
        tests/unit/test_logging_level_toggle.py -v
```

---

## Phase 6: Polish & Documentation

*Cross-cutting concerns and final documentation*

---

### T018: Create comprehensive logging reference guide (1 hour)

**Objective**: Single source of truth for all logging behavior

**Description**:
- Consolidate into one reference document:
  - What logs appear and when
  - Expected timings (5s for process start, 10s for command send, 30s for response)
  - Log levels (INFO for important events, DEBUG for detailed flow)
  - Emoji meanings (✅=success, ❌=error, 📨=message, 📦=output, 🔨=command, 🔌=connection)
  - Context fields (session ID, user ID, connection ID, PID)
- Include examples for:
  - Successful message processing (full flow)
  - Error scenarios (connection failed, process crashed, etc.)
  - Performance debugging (slow message processing)

**Files Created/Modified**:
- Create `backend/LOGGING_REFERENCE.md` (main reference)
- Update `backend/LOGGING_GUIDE.md` (link to reference)
- Update `backend/WEBSOCKET_DEBUG_GUIDE.md` (include logging examples)

**Acceptance Criteria**:
- ✅ Complete reference for all logging in the system
- ✅ Clear examples for all common scenarios
- ✅ Troubleshooting guide for common issues
- ✅ Performance debugging tips

**Dependencies**: T005-T017 (all testing/documentation complete)

---

### T019: Create developer quickstart for testing (1 hour)

**Objective**: Enable developers to quickly test the feature

**Description**:
- Create `backend/tests/integration/QUICKSTART.md` with:
  - How to run all tests for this feature
  - How to run tests for specific user story
  - How to run just logging tests (fast validation)
  - How to see example log output
  - How to test with real Claude vs mocked Claude
  - Interpretation of test output
- Include commands:
  ```bash
  # Run all tests
  pytest tests/ -k "logging" -v

  # Run just US1 tests
  pytest tests/integration/test_websocket_logging.py -v

  # Run just US2 tests
  pytest tests/integration/test_websocket_lifecycle.py \
          tests/integration/test_claude_process_logging.py -v

  # Run just US3 tests
  pytest tests/integration/test_console_output.py -v
  ```

**Files Created**:
- `backend/tests/integration/QUICKSTART.md`

**Acceptance Criteria**:
- ✅ Clear commands for running tests
- ✅ Explains what each test verifies
- ✅ Includes interpretation guide
- ✅ Can be followed by new developer

**Dependencies**: T004-T017 (all tests exist)

---

### T020: Update project README with feature (30 min)

**Objective**: Document the feature in main project documentation

**Description**:
- Update `backend/README.md` (or create one if missing):
  - Add section: "Logging & Debugging"
  - Link to LOGGING_REFERENCE.md
  - Link to CLAUDE_PROCESS_LIFECYCLE.md
  - Link to WEBSOCKET_DEBUG_GUIDE.md
  - Link to quickstart guide
- Add feature status: "✅ Complete - Full logging visibility"

**Files Modified**:
- `backend/README.md`

**Acceptance Criteria**:
- ✅ Logging section clearly documents feature
- ✅ Links to detailed documentation
- ✅ Clear entry point for developers

**Dependencies**: T018, T013, T017

---

### T021: Verify all tests pass (30 min)

**Objective**: Final validation that all tests pass

**Description**:
- Run complete test suite:
  ```bash
  cd backend
  pytest tests/ -v --tb=short
  ```
- Verify:
  - All unit tests pass
  - All integration tests pass
  - All logging tests pass
  - Code coverage for new tests is adequate
- Fix any failing tests
- Generate coverage report

**Acceptance Criteria**:
- ✅ All tests pass (100% pass rate)
- ✅ No warnings or errors
- ✅ Coverage report generated
- ✅ Coverage is >80% for logging-related code

**Files**: Test files (no changes, just verification)

**Dependencies**: T004-T020 (all tests exist)

---

### T022: Final documentation review and cleanup (30 min)

**Objective**: Ensure all documentation is complete and consistent

**Description**:
- Review all created/modified documentation:
  - LOGGING_REFERENCE.md - complete?
  - CLAUDE_PROCESS_LIFECYCLE.md - clear?
  - LOGGING_GUIDE.md - updated?
  - WEBSOCKET_DEBUG_GUIDE.md - current?
  - README.md - links work?
  - Quickstart guide - can someone follow it?
- Fix any inconsistencies or unclear sections
- Verify all links work
- Proofread for clarity

**Acceptance Criteria**:
- ✅ All documentation consistent
- ✅ No broken links
- ✅ Clear language throughout
- ✅ Ready for release

**Dependencies**: T018, T013, T017, T020

---

### Checkpoint: Feature Complete ✅

**At this point**:
- ✅ All 3 user stories implemented and tested
- ✅ All 22 tasks completed
- ✅ Comprehensive test coverage
- ✅ Complete documentation
- ✅ Ready for production deployment

**Final Verification**:
```bash
cd backend

# Run all tests
pytest tests/ -v

# Check logging works
python3.12 -c "from src.logging_config import setup_logging; logger = setup_logging(); print('✅ Logging ready')"

# Start backend and verify logs
# (See QUICKSTART.md for manual testing steps)
```

---

## Task Summary & Metrics

### By Phase

| Phase | Name | Tasks | Hours | Status |
|-------|------|-------|-------|--------|
| 2 | Foundational | T001-T003 | 2.5 | Foundation |
| 3 | User Story 1 | T004-T008 | 5 | Core Feature |
| 4 | User Story 2 | T009-T013 | 5 | Debugging |
| 5 | User Story 3 | T014-T017 | 3.5 | UX |
| 6 | Polish | T018-T022 | 3 | Finalization |
| **Total** | | **22** | **18.5** | Ready |

### By Type

| Type | Count | Hours |
|------|-------|-------|
| Integration Tests | 7 | 7 |
| Unit Tests | 4 | 3.5 |
| Documentation | 5 | 5 |
| Verification | 5 | 2.5 |
| Polish | 1 | 0.5 |

### By User Story

| Story | Tasks | Hours | Deliverables |
|-------|-------|-------|--------------|
| US1: Message Response | T004-T008 | 5 | Tests + Documentation |
| US2: Process Lifecycle | T009-T013 | 5 | Tests + Documentation |
| US3: Console Cleanliness | T014-T017 | 3.5 | Tests + Documentation |

---

## Parallel Execution Example

### MVP Path (User Story 1 Only) - 5-6 hours
```
T004 (1h) - Fixtures
  ├─ T005 (2h) - Integration test [P]
  ├─ T006 (1h) - E2E test [P]
  └─ T008 (1h) - Unit test [P]
  └─ T007 (0.5h) - Documentation

Total: ~5-6 hours to complete US1
```

### Full Feature Path - 18-20 hours
```
T001-T003 (2.5h) - Foundational checks
  ├─ Phase 3 (5h) - US1 [Can deploy alone]
  │   └─ Phase 4 (5h) - US2 [Can deploy alone]
  │       └─ Phase 5 (3.5h) - US3 [Can deploy alone]
  │           └─ Phase 6 (3h) - Polish & Docs
```

Within each phase, many tasks can run in parallel [P]:
- T005, T006, T008 (message flow testing) - parallel
- T009, T010, T011, T012 (process logging testing) - parallel
- T014, T015, T016 (console output testing) - parallel

---

## Success Criteria & Verification

### Before Merging
- ✅ All 22 tasks completed
- ✅ All tests pass (0 failures)
- ✅ Code review completed
- ✅ Documentation reviewed

### Before Release
- ✅ Manual testing with real Claude Code completed
- ✅ Logging verified in production-like environment
- ✅ Performance targets met (response within 30s)
- ✅ Operator documentation reviewed and approved

### Known Working
- ✅ WebSocket logging infrastructure (from commit 93a3c90)
- ✅ Claude process logging (from multiple commits)
- ✅ SQLAlchemy logging suppression (from commit df95e0a)
- ✅ SQLAlchemy echo disabled (from commit ce4fde3)
- ✅ Configuration management (from commit 042189c)

---

## Next Steps

### To Start Implementation
1. Choose MVP scope (just US1) or full scope (all 3 stories)
2. Run T001-T003 (foundational checks) - confirm infrastructure
3. Run T004 (create fixtures) - test infrastructure
4. Run T005-T008 in parallel (complete US1)
5. Proceed with US2, US3 in sequence
6. Run T021-T022 (final verification)

### To Execute Tasks
```bash
# Start backend
cd backend && python3.12 -m uvicorn src.main:app --reload

# In another terminal, run tests
pytest tests/ -v --tb=short

# Monitor logs
tail -f logs/app.log

# See QUICKSTART.md for detailed testing procedures
```

---

## References

- **Feature Specification**: `/specs/002-claude-code/spec.md`
- **Implementation Plan**: `/specs/002-claude-code/plan.md`
- **Constitution**: `.specify/memory/constitution.md`
- **Related Commits**: 93a3c90, df95e0a, 042189c, ce4fde3

