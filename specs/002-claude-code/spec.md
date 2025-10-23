# Feature Specification: Debug and Fix WebSocket/Claude Code Communication

**Feature Branch**: `002-claude-code`
**Created**: 2025-10-22
**Status**: Draft
**Input**: User description: "前台登入後使用對話問問題,後台沒有任何回應,也不知道有沒有啟動claude code"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - User Sends Message and Receives Claude Response (Priority: P1)

A logged-in user opens the chat interface, types a question or command, and expects Claude Code to process it and return a response within a reasonable timeframe.

**Why this priority**: This is the core value proposition of the system. Without this working, the application is non-functional. This is blocking all users.

**Independent Test**: A user can send a message through the web interface, see backend logs confirming Claude Code process started, see the command was sent to Claude, and receive a response with visible output chunks.

**Acceptance Scenarios**:

1. **Given** user is logged in and WebSocket connection is established, **When** user sends a message "hello", **Then** backend logs show "Claude process started" within 5 seconds AND backend logs show "Command sent to Claude" within 10 seconds AND user receives output within 30 seconds

2. **Given** Claude Code process is running, **When** user sends a command, **Then** backend logs show each output chunk received with sequence numbers AND user sees output incrementally on frontend

3. **Given** user sends a message, **When** backend encounters an error, **Then** user receives an error message explaining what went wrong AND backend logs show the error with full stack trace

---

### User Story 2 - Backend Logs Show Claude Process Lifecycle (Priority: P1)

Backend operators need visibility into whether Claude Code processes are starting, running, and stopping correctly. Currently, backend shows no logs about Claude process status.

**Why this priority**: Without logs, we cannot debug why messages aren't being processed. This is critical for troubleshooting the P1 issue.

**Independent Test**: When a user initiates a chat session, backend logs clearly show: (1) session created, (2) Claude process starting with path and PID, (3) process started successfully or failed with reason, (4) commands being sent, (5) output being read, (6) cleanup on disconnect.

**Acceptance Scenarios**:

1. **Given** a new WebSocket connection is established, **When** checking logs, **Then** logs show connection accepted with session ID and user ID within first 5 entries

2. **Given** Claude process needs to start, **When** checking logs, **Then** logs show at minimum: executable path being verified, working directory, PID of started process, "✅ Claude process started successfully"

3. **Given** user sends a command, **When** checking logs, **Then** logs show command text, confirmation it was sent to Claude, and each output chunk received

4. **Given** WebSocket disconnects, **When** checking logs, **Then** logs show cleanup with connection ID and confirm resources released

---

### User Story 3 - Console Output is Clean and Readable (Priority: P2)

Backend console output is currently flooded with SQLAlchemy SQL queries, making it impossible to see WebSocket and Claude logs. Developers need clean, readable output focused on application-level events.

**Why this priority**: Developers need to see what's happening. SQL logs can be accessed from log files if needed, but console should show only relevant application logs.

**Independent Test**: When backend starts and a user sends a message, console output shows only application events (no SQL SELECT/INSERT/UPDATE) and all WebSocket + Claude events are visible without scrolling through hundreds of lines.

**Acceptance Scenarios**:

1. **Given** backend is running with DEBUG=true, **When** checking console, **Then** no "sqlalchemy.engine.Engine SELECT/INSERT/UPDATE" lines appear

2. **Given** user sends a message and Claude processes it, **When** checking console, **Then** all WebSocket lifecycle events and Claude process events are visible within 100 lines of output

---

### Edge Cases

- What happens when Claude Code executable is not found or not in PATH?
- What happens when Claude process crashes mid-execution?
- What happens when WebSocket connection drops while waiting for Claude output?
- What happens when Claude takes longer than expected to respond (timeout handling)?
- What happens when user sends an empty message or invalid command?
- What happens when backend database is unavailable during message save?

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST display backend logs showing Claude Code process initialization when a new WebSocket connection is established
- **FR-002**: System MUST log the Claude executable path, working directory, and process ID (PID) when starting the process
- **FR-003**: System MUST log success/failure of Claude process startup with clear error messages if it fails
- **FR-004**: System MUST log each command being sent to Claude with a summary (full text or first N characters)
- **FR-005**: System MUST log each output chunk received from Claude with sequence numbers and chunk size
- **FR-006**: System MUST log execution time for each command (time from send to completion)
- **FR-007**: System MUST suppress SQLAlchemy SQL query logs from console output while preserving them in log files
- **FR-008**: System MUST handle the case where Claude Code executable path is missing or invalid and log the error clearly
- **FR-009**: System MUST handle Claude process crashes and log the error with stack trace
- **FR-010**: System MUST implement WebSocket message validation and log invalid messages with reason
- **FR-011**: System MUST detect tool approval requests from Claude and log them clearly
- **FR-012**: System MUST support toggling SQL logging level via environment variable without code changes
- **FR-013**: System MUST log all WebSocket connection/disconnection events with timestamps and session information

### Key Entities *(include if feature involves data)*

- **Session**: Represents a user's chat session, includes session ID, user ID, status (active/inactive), creation timestamp
- **Message**: Represents a message in the session, includes message ID, session ID, role (user/assistant), content, timestamp, sequence number
- **Message Chunk**: Represents streamed output from Claude, includes chunk sequence number, content, timestamp
- **Claude Process**: Internal representation of running Claude Code process, includes PID, session ID, status, start time

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: When a user sends a message, backend logs show "Claude process started" within 5 seconds (currently missing, target: 100% of sessions)
- **SC-002**: When Claude processes a message, at least 3 separate logging events appear (process start, command sent, output chunks) (currently 0, target: minimum 3 per message)
- **SC-003**: Backend console output contains zero "sqlalchemy.engine" SQL query logs while processing user messages (currently 100% SQL noise, target: 0%)
- **SC-004**: All WebSocket lifecycle events (connect, accept, disconnect) are logged with session/user context (currently missing, target: 100% of connections have 3+ log entries)
- **SC-005**: Complete message flow is traceable in logs: user message → Claude command sent → output received → response complete (currently impossible to trace, target: 100% of messages have complete trace)
- **SC-006**: Claude process errors and failures are logged with actionable error messages and stack traces (currently missing, target: 100% of errors are logged with details)
- **SC-007**: User perceives visible response within 30 seconds of sending message (user can see backend working through logs and output)

## Assumptions

- Claude Code executable is properly installed at the path specified in `CLAUDE_CODE_PATH` environment variable
- PostgreSQL database is available and accessible with configured credentials
- WebSocket connections are properly established and authenticated before messages are sent
- "No response" means either: (a) frontend doesn't receive any output, or (b) output is received but incomplete/garbled
- Log files are being written to the location configured in `LOG_DIR` setting
- The issue is not network-related (frontend can connect, database can save messages)

## Constraints & Assumptions About Implementation

- Logging must use Python's standard `logging` module to be controlled by configuration
- Do not require code changes to toggle SQL logging (environment variable should be sufficient)
- Log messages should use emoji indicators for quick visual scanning (✅, ❌, 🔨, 📦, etc.)
- Each log entry should include relevant context (session ID, user ID, connection ID) for traceability

## Out of Scope

- Implementing new Claude Code features or functionality
- Frontend UI improvements
- Performance optimization beyond debugging visibility
- User authentication changes
- Database schema changes
