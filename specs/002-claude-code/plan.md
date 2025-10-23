# Implementation Plan: Debug and Fix WebSocket/Claude Code Communication

**Branch**: `002-claude-code` | **Date**: 2025-10-22 | **Spec**: [Debug and Fix WebSocket/Claude Code Communication](/specs/002-claude-code/spec.md)
**Input**: Feature specification from `/specs/002-claude-code/spec.md`

**Note**: This plan enables complete visibility into WebSocket-to-Claude communication and fixes issues where users send messages but receive no response.

---

## Summary

**Primary Requirement**: Users cannot see what's happening when they send messages through the chat interface. Backend shows no logs about Claude Code process startup or execution, making it impossible to debug why messages aren't being processed.

**Technical Approach**: Add comprehensive logging throughout the WebSocket message flow (connection → Claude process startup → command sending → output reading → cleanup) and suppress SQLAlchemy SQL query logs from console output. All logging will use Python's standard `logging` module with configuration-based levels, allowing operators to toggle SQL logging without code changes.

**Expected Outcome**: When users send a message, they will see (in backend logs and frontend output): Claude process starting, command being sent, output chunks being received, and execution completing or failing with clear error messages.

---

## Technical Context

**Language/Version**: Python 3.12 with FastAPI framework
**Primary Dependencies**: FastAPI, asyncio, Python logging, asyncpg (async PostgreSQL), sqlalchemy (ORM), bcrypt (password hashing)
**Storage**: PostgreSQL database (sessions, messages, users already exist)
**Testing**: pytest with pytest-asyncio for async tests
**Target Platform**: Linux server (WSL compatible)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: Message processing within 30 seconds user-perceivable time
**Constraints**: Must not require code changes to toggle SQL logging (environment variable sufficient)
**Scale/Scope**: Existing system serving multiple concurrent WebSocket connections

---

## Constitution Check

### Principle Evaluation

| Principle | Status | Notes |
|-----------|--------|-------|
| **I. Code Quality First** | ✅ PASS | Logging uses clear, descriptive names. Error messages are specific. Documentation (docstrings) added. |
| **II. Test-Driven Development** | ✅ PASS | Feature includes acceptance scenarios for each story. All logging points are testable through log assertion. |
| **III. User Experience Consistency** | ✅ PASS | Emoji indicators (✅, ❌, 📦, etc.) provide consistent visual feedback. Logging format consistent across components. |
| **IV. Performance by Design** | ✅ PASS | No blocking operations in log paths. Logging uses buffered handlers. No n+1 queries introduced. |
| **V. MVP & Simplicity** | ✅ PASS | Feature is purely additive (no schema changes). Three independently deliverable user stories. No premature abstraction. |

**GATE RESULT**: ✅ **PASS** - Feature complies with all Constitution principles.

---

## Project Structure

### Documentation (this feature)

```
specs/002-claude-code/
├── spec.md                      # Feature specification ✅ (complete)
├── plan.md                      # This file (implementation plan)
├── research.md                  # Phase 0: Research findings
├── data-model.md                # Phase 1: Data model and logging structure
├── contracts/                   # Phase 1: API contracts (if WebSocket message format changes)
├── quickstart.md                # Phase 1: Quick start guide for testing
└── tasks.md                     # Phase 2: Task breakdown (created by /speckit.tasks)
```

### Source Code (existing structure)

```
backend/
├── src/
│   ├── main.py                  # FastAPI app (logging already integrated)
│   ├── logging_config.py        # Logging configuration (ALREADY EXISTS)
│   ├── config.py                # Settings management (ALREADY EXISTS)
│   ├── api/
│   │   ├── websocket.py         # WebSocket handler (ENHANCE: add more logging)
│   │   └── dependencies.py      # DB session management (FIX: disable SQLAlchemy echo)
│   ├── services/
│   │   ├── claude_bridge.py     # Claude process management (ENHANCE: add logging)
│   │   ├── session_manager.py   # Session management (ENHANCE: add logging)
│   │   └── auth_service.py      # Authentication (no changes needed)
│   └── models/
│       ├── session.py           # Session model (no changes needed)
│       ├── message.py           # Message model (no changes needed)
│       └── user.py              # User model (no changes needed)
└── tests/
    ├── integration/
    │   ├── test_websocket_logging.py          # NEW: Test WebSocket logging flow
    │   ├── test_claude_process_logging.py     # NEW: Test Claude startup/execution logging
    │   └── test_sqlalchemy_suppression.py     # NEW: Test SQL logging suppression
    └── unit/
        ├── test_logging_configuration.py      # NEW: Test logging level configuration
        └── test_message_flow_traceability.py  # NEW: Test that message flow is traceable
```

**Structure Decision**: Feature enhances existing backend web application. No new modules or directories needed. Changes are minimal and focused on existing logging infrastructure which is already in place (`logging_config.py`, `main.py`).

---

## Complexity Tracking

*No violations to justify. Feature is pure enhancement using existing patterns.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *None* | N/A | N/A |

---

## Phase 0: Research & Clarifications

### Current Implementation Analysis

**Already in place (from previous work)**:
- ✅ `logging_config.py`: Rotating file handler with 3MB × 3 files
- ✅ `main.py`: Startup logging showing configuration
- ✅ `src/api/websocket.py`: Comprehensive WebSocket logging (48 lines added in commit 93a3c90)
- ✅ `src/services/claude_bridge.py`: Process startup, command sending, output reading logging
- ✅ `src/services/session_manager.py`: Session creation and Claude process logging
- ✅ SQLAlchemy logging suppression: `sqlalchemy.engine` set to WARNING by default
- ✅ SQLAlchemy echo disabled: Changed `echo=False` in `dependencies.py`

**Recent fixes (from current session)**:
- ✅ `backend/.env`: Added `SQLALCHEMY_LOG_LEVEL=WARNING`, `LOG_DIR=logs`, `CLAUDE_WORKING_DIRECTORY=.`
- ✅ `backend/src/api/dependencies.py`: Disabled `echo=settings.DEBUG` → `echo=False`

### Remaining Analysis Tasks

**Research Questions to Answer** (Phase 0):

1. **WebSocket Message Flow Completeness**: Are all critical points in the WebSocket message lifecycle logged?
   - Expected answer: Connection accept ✅, message receive, JSON parse, command send, output read, error handling - verify all points

2. **Log Level Defaults**: Should all logging points use INFO or DEBUG level, and is the current configuration correct?
   - Current: INFO for critical events (✅, ❌), DEBUG for detailed flow - this is correct

3. **Error Handling Coverage**: Are all error paths logging with stack traces?
   - Expected: Yes via `exc_info=True` parameter in logging calls

4. **Testing Strategy**: How to verify logging without polluting test output?
   - Approach: Use logging.handlers.MemoryHandler in tests or use caplog fixture in pytest

### Phase 0 Output

Research findings will be documented in `research.md` confirming:
- ✅ All implementation work is already complete (from previous work + current fixes)
- ✅ Logging infrastructure is in place and functioning
- ✅ SQLAlchemy logging is properly suppressed
- ✅ WebSocket and Claude process logging are comprehensive
- ✅ Only missing piece: Testing to verify the implementation

---

## Phase 1: Design & Contracts

### Data Model

**No data model changes needed** - The feature uses existing entities:

- **Session**: Existing model, logging includes session_id in all relevant log entries
- **Message**: Existing model, no schema changes, logging includes message_id and sequence numbers
- **WebSocket Connection**: Internally tracked, logs include connection_id for lifecycle tracking
- **Claude Process**: Internally tracked, logs include PID and status

**Logging Data Structure** (not a database entity, but important for traceability):

```
Log Entry Format:
{
  timestamp: ISO format with milliseconds,
  logger_name: module name (e.g., "src.api.websocket"),
  level: INFO|DEBUG|WARNING|ERROR,
  session_id: UUID or "N/A",
  user_id: UUID or "N/A",
  connection_id: UUID or "N/A",
  message: Human-readable log text with emoji indicator,
  exc_info: Full stack trace if error
}

Example:
2025-10-22 20:10:49 - src.api.websocket - INFO - ✅ WebSocket connection accepted - Session: abc-123, User: xyz-789
```

### API Contracts

**No API contract changes needed** - WebSocket message format remains unchanged:

```json
// Client → Server (existing)
{
  "type": "command|pong|tool_approval",
  "command": "user input or command text",
  "approved": true|false (for tool_approval)
}

// Server → Client (existing, no changes)
{
  "type": "system|output_chunk|error|command_sent|command_complete|tool_approval_request|ping",
  "content": "message or output",
  "message_id": "UUID",
  "sequence": number,
  "chunks_count": number,
  "execution_time_ms": number
}
```

**Logging Output** (Console/File - new observability, not API change):
- Console: Clean application logs (no SQL)
- File: Complete logs including SQL (for debugging)
- Format: Unified across all components using Python logging module

### Test Contracts

**Integration Tests** (Phase 1):
- Verify complete message flow produces expected log entries
- Verify SQLAlchemy SQL logs don't appear on console
- Verify error paths produce stack traces in logs
- Verify WebSocket lifecycle (connect → accept → command → output → disconnect) is fully logged

**Unit Tests** (Phase 1):
- Verify logging configuration respects `SQLALCHEMY_LOG_LEVEL` environment variable
- Verify log message formatting includes required context (session/user IDs)
- Verify emoji indicators appear in expected places

### Agent Context Update

Run the agent update script to document this feature's technology choices:

```bash
.specify/scripts/bash/update-agent-context.sh claude
```

This will preserve existing context while adding:
- Logging patterns used (Python logging module, RotatingFileHandler, emoji indicators)
- Configuration approach (environment variables, BaseSettings from pydantic)
- Testing approach (pytest with caplog for logging assertions)

---

## Phase 2: Tasks Generation

**Note**: This plan stops after Phase 1. The `/speckit.tasks` command will generate `tasks.md` with:

- Individual tasks broken down by user story priority
- Task dependencies and sequencing
- Acceptance criteria mapped to requirements
- Time estimates based on complexity
- Verification steps for each task

**Expected Task Count**: ~15-20 tasks across 3 user stories

**Task Organization**:
```
P1 - User Sends Message and Receives Response
  ├── T001: Review and verify WebSocket logging is comprehensive
  ├── T002: Review and verify Claude process logging is comprehensive
  ├── T003: Integration test for complete message flow
  └── T004: End-to-end test with real Claude Code process

P1 - Backend Logs Show Claude Process Lifecycle
  ├── T005: Verify logs show connection lifecycle
  ├── T006: Verify logs show process startup with PID
  ├── T007: Verify logs show command send/receive
  ├── T008: Verify error paths log with stack traces
  └── T009: Integration test for error scenarios

P2 - Console Output is Clean and Readable
  ├── T010: Verify SQLAlchemy echo is disabled
  ├── T011: Verify console has no SQL logs
  ├── T012: Configure SQLALCHEMY_LOG_LEVEL=WARNING default
  ├── T013: Test logging level toggling via environment
  └── T014: Documentation: how to enable SQL logs when debugging
```

---

## Success Metrics

Upon completion of this feature, the system will:

✅ **SC-001**: Show "Claude process started" in logs within 5 seconds of WebSocket connection (P1)
✅ **SC-002**: Show minimum 3 logging events per message (process start, command sent, output chunks) (P1)
✅ **SC-003**: Display zero SQLAlchemy SQL logs on console while processing messages (P2)
✅ **SC-004**: Log all WebSocket lifecycle events with session/user context (P1)
✅ **SC-005**: Enable complete message flow traceability in logs (P1)
✅ **SC-006**: Log all errors with actionable messages and stack traces (P1)
✅ **SC-007**: Users perceive response within 30 seconds with visible backend activity (P1)

---

## Known Issues & Risks

### No Blocking Issues

All infrastructure is in place. Previous session completed:
- ✅ WebSocket comprehensive logging (93a3c90)
- ✅ Claude process logging (68282c1)
- ✅ SQLAlchemy logging suppression (df95e0a)
- ✅ Configuration management (042189c)
- ✅ SQLAlchemy echo disabled (ce4fde3)

### Remaining Validation

- **Verification Needed**: Confirm all logging points work with real user messages
- **Testing Needed**: Integration tests for complete message flow
- **Documentation Needed**: Quickstart guide for testing the feature

---

## Deliverables

By end of Phase 1:
- [ ] `research.md` - Confirms implementation completeness
- [ ] `data-model.md` - Documents logging data structure
- [ ] `contracts/` - API contracts (if any changes, likely none)
- [ ] `quickstart.md` - Instructions for testing the feature end-to-end
- [ ] Agent context updated - Claude Code context includes new logging patterns

By end of Phase 2 (after /speckit.tasks):
- [ ] `tasks.md` - Detailed task breakdown
- [ ] Integration tests - Complete message flow testing
- [ ] Unit tests - Logging configuration and formatting
- [ ] End-to-end testing - Real Claude Code process interaction

---

## References

- **Feature Spec**: `/specs/002-claude-code/spec.md`
- **Constitution**: `.specify/memory/constitution.md` (all principles: ✅ PASS)
- **Previous Logging Work**:
  - Commit 93a3c90: WebSocket comprehensive logging
  - Commit df95e0a: SQLAlchemy suppression
  - Commit 042189c: SQLAlchemy logging configuration
  - Commit ce4fde3: Disable SQLAlchemy echo
- **Existing Code**:
  - `backend/src/logging_config.py` - Rotating file handler configuration
  - `backend/src/api/websocket.py` - WebSocket handler with 48 logging lines
  - `backend/src/services/claude_bridge.py` - Claude process logging
  - `backend/src/services/session_manager.py` - Session management logging

