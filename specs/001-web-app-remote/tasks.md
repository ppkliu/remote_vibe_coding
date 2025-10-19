# Tasks: Claude Code Remote Web Controller

**Input**: Design documents from `/specs/001-web-app-remote/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included following TDD principle - write tests FIRST, ensure they FAIL, then implement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Web app**: `backend/src/`, `frontend/src/`
- Tests: `backend/tests/`, `frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Initialize backend project with uv and pyproject.toml configuration
- [X] T002 Initialize frontend project with Vite, Vue 3, TypeScript, and TailwindCSS
- [X] T003 [P] Setup docker-compose.yml with PostgreSQL service
- [X] T004 [P] Create backend/.env.example with all required environment variables
- [X] T005 [P] Create frontend/.env.example with VITE_API_URL and VITE_WS_URL
- [X] T006 [P] Setup ESLint and TypeScript strict mode for frontend
- [X] T007 [P] Setup Ruff, Black, and mypy for backend Python code
- [X] T008 Initialize Alembic for database migrations in backend/
- [X] T009 [P] Setup Vitest configuration in frontend/vitest.config.ts
- [X] T010 [P] Setup pytest and pytest-asyncio configuration in backend/pyproject.toml
- [X] T011 Initialize Shadcn-vue and add base components (Button, Input, Card, ScrollArea)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema and Models

- [X] T012 Create User SQLAlchemy model in backend/src/models/user.py with bcrypt password hashing
- [X] T013 Create Session SQLAlchemy model in backend/src/models/session.py with status enum
- [X] T014 Create Message SQLAlchemy model in backend/src/models/message.py with JSONB metadata
- [X] T015 Create ClaudeProcess SQLAlchemy model in backend/src/models/claude_process.py
- [X] T016 Generate Alembic migration for initial schema (users, sessions, messages, claude_processes)
- [ ] T017 Apply database migration with alembic upgrade head

### Authentication Foundation

- [X] T018 [P] Create Pydantic schemas for User in backend/src/schemas/user.py
- [X] T019 [P] Create Pydantic schemas for auth requests/responses in backend/src/schemas/auth.py
- [X] T020 Implement JWT token generation and validation in backend/src/services/auth_service.py
- [X] T021 Implement password hashing with bcrypt in backend/src/services/auth_service.py
- [X] T022 Create POST /api/v1/auth/register endpoint in backend/src/api/auth.py
- [X] T023 Create POST /api/v1/auth/login endpoint in backend/src/api/auth.py
- [X] T024 Create POST /api/v1/auth/refresh endpoint in backend/src/api/auth.py
- [X] T025 Create authentication dependency for protected routes in backend/src/api/dependencies.py

### FastAPI Application Setup

- [X] T026 Create FastAPI app instance in backend/src/main.py with CORS configuration
- [X] T027 Setup database connection pool with SQLAlchemy async engine in backend/src/config.py
- [X] T028 Create database session dependency in backend/src/api/dependencies.py
- [X] T029 Register authentication routes in backend/src/main.py
- [X] T030 Add health check endpoint GET /health in backend/src/main.py

### Frontend Base Application

- [X] T031 Create Vue Router configuration in frontend/src/router/index.ts with routes
- [X] T032 Setup Pinia store in frontend/src/main.ts
- [X] T033 [P] Create TypeScript types for User in frontend/src/types/user.ts
- [X] T034 [P] Create TypeScript types for Session in frontend/src/types/session.ts
- [X] T035 [P] Create TypeScript types for Message in frontend/src/types/message.ts
- [X] T036 Create auth Pinia store in frontend/src/stores/auth.ts with login/logout actions
- [X] T037 Create HTTP API client in frontend/src/services/api.ts with axios
- [X] T038 Create authentication service in frontend/src/services/auth.ts
- [X] T039 Create LoginView.vue in frontend/src/views/LoginView.vue
- [X] T040 Create RegisterView.vue in frontend/src/views/RegisterView.vue (optional for MVP)
- [X] T041 Create App.vue root component with router-view
- [X] T042 Setup route guards for authentication in frontend/src/router/index.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Remote Command Execution (Priority: P1) 🎯 MVP

**Goal**: Enable sending commands to Claude Code and displaying responses

**Independent Test**: Start Claude Code, open web interface, send command, verify response appears

### Tests for User Story 1 ⚠️ WRITE FIRST

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T043 [P] [US1] Contract test for WebSocket command message format in backend/tests/contract/test_websocket_protocol.py
- [ ] T044 [P] [US1] Contract test for POST /api/v1/sessions endpoint in backend/tests/contract/test_sessions_api.py
- [ ] T045 [P] [US1] Integration test for session creation and Claude process startup in backend/tests/integration/test_session_lifecycle.py
- [ ] T046 [P] [US1] Integration test for command execution flow in backend/tests/integration/test_command_execution.py
- [ ] T047 [P] [US1] Unit test for useWebSocket composable in frontend/tests/unit/composables/useWebSocket.spec.ts
- [ ] T048 [P] [US1] Unit test for CommandInput component in frontend/tests/unit/components/CommandInput.spec.ts

### Backend Implementation for User Story 1

- [X] T049 [P] [US1] Create Pydantic schemas for Session in backend/src/schemas/session.py
- [X] T050 [P] [US1] Create Pydantic schemas for Command/Message in backend/src/schemas/command.py
- [X] T051 [US1] Implement ClaudeBridgeService in backend/src/services/claude_bridge.py for subprocess management
- [X] T052 [US1] Implement SessionManager in backend/src/services/session_manager.py for session lifecycle
- [X] T053 [US1] Create POST /api/v1/sessions endpoint in backend/src/api/sessions.py
- [X] T054 [US1] Create GET /api/v1/sessions endpoint in backend/src/api/sessions.py
- [X] T055 [US1] Create GET /api/v1/sessions/{id} endpoint in backend/src/api/sessions.py
- [X] T056 [US1] Implement WebSocket endpoint WS /ws/{session_id} in backend/src/api/websocket.py
- [X] T057 [US1] Add WebSocket authentication and session validation in backend/src/api/websocket.py
- [X] T058 [US1] Implement command message handling in WebSocket handler
- [X] T059 [US1] Implement output streaming from Claude process to WebSocket
- [X] T060 [US1] Add error handling for process crashes in backend/src/services/claude_bridge.py

### Frontend Implementation for User Story 1

- [X] T061 [P] [US1] Create session Pinia store in frontend/src/stores/session.ts
- [X] T062 [P] [US1] Create messages Pinia store in frontend/src/stores/messages.ts
- [X] T063 [P] [US1] Create connection Pinia store in frontend/src/stores/connection.ts
- [X] T064 [US1] Create WebSocket client service in frontend/src/services/websocket.ts
- [X] T065 [US1] Create useWebSocket composable in frontend/src/composables/useWebSocket.ts
- [X] T066 [US1] Create useSession composable in frontend/src/composables/useSession.ts
- [X] T067 [P] [US1] Create CommandInput.vue component in frontend/src/components/CommandInput.vue
- [X] T068 [P] [US1] Create OutputDisplay.vue component in frontend/src/components/OutputDisplay.vue
- [X] T069 [P] [US1] Create ConnectionStatus.vue component in frontend/src/components/ConnectionStatus.vue
- [X] T070 [US1] Create HomeView.vue (main chat interface) in frontend/src/views/HomeView.vue
- [X] T071 [US1] Connect HomeView to stores and composables
- [X] T072 [US1] Add loading indicator during command processing in OutputDisplay.vue
- [X] T073 [US1] Implement conversation history display in OutputDisplay.vue
- [X] T074 [US1] Add command submission on Enter key in CommandInput.vue

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Real-time Output Streaming (Priority: P2)

**Goal**: Display Claude Code output progressively as it's generated

**Independent Test**: Send command with long output, verify chunks appear progressively

### Tests for User Story 2 ⚠️ WRITE FIRST

- [ ] T075 [P] [US2] Contract test for output_chunk WebSocket message in backend/tests/contract/test_websocket_protocol.py
- [ ] T076 [P] [US2] Integration test for streaming output in backend/tests/integration/test_streaming.py
- [ ] T077 [P] [US2] Unit test for streaming output display in frontend/tests/unit/components/OutputDisplay.spec.ts

### Backend Implementation for User Story 2

- [X] T078 [US2] Implement async generator for Claude stdout streaming in backend/src/services/claude_bridge.py
- [X] T079 [US2] Add output chunking logic with sequence numbers in backend/src/api/websocket.py
- [X] T080 [US2] Implement output_chunk message sending via WebSocket
- [X] T081 [US2] Add command_complete message after final chunk

### Frontend Implementation for User Story 2

- [X] T082 [US2] Update useWebSocket to handle output_chunk messages
- [X] T083 [US2] Implement progressive message appending in messages store
- [X] T084 [US2] Add auto-scroll logic in OutputDisplay.vue (preserve position if scrolled up)
- [X] T085 [US2] Add visual indicator for streaming in progress
- [X] T086 [US2] Display execution time after command completion

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Session Management and Reconnection (Priority: P2)

**Goal**: Maintain sessions across disconnections and browser restarts

**Independent Test**: Connect, send commands, disconnect network, reconnect, verify context preserved

### Tests for User Story 3 ⚠️ WRITE FIRST

- [ ] T087 [P] [US3] Integration test for session persistence in backend/tests/integration/test_session_persistence.py
- [ ] T088 [P] [US3] Integration test for WebSocket reconnection in backend/tests/integration/test_reconnection.py
- [ ] T089 [P] [US3] Unit test for reconnection logic in frontend/tests/unit/composables/useWebSocket.spec.ts

### Backend Implementation for User Story 3

- [ ] T090 [US3] Implement session state preservation during disconnections in backend/src/services/session_manager.py
- [ ] T091 [US3] Add session cleanup job for sessions idle >24 hours
- [ ] T092 [US3] Implement WebSocket ping/pong heartbeat (30-second interval)
- [ ] T093 [US3] Store WebSocket connection ID in Session model
- [ ] T094 [US3] Implement GET /api/v1/sessions/{id}/messages for history retrieval

### Frontend Implementation for User Story 3

- [X] T095 [US3] Implement exponential backoff reconnection in useWebSocket.ts (1s, 2s, 4s, 8s, 30s)
- [X] T096 [US3] Add reconnecting status indicator in ConnectionStatus.vue
- [X] T097 [US3] Persist active session ID to localStorage in session store
- [X] T098 [US3] Implement session resumption on app load in HomeView.vue
- [X] T099 [US3] Fetch message history on session resume
- [X] T100 [US3] Add "Reconnect" button when connection fails after 5 attempts
- [ ] T101 [US3] Display notification when Claude Code process restarts

**Checkpoint**: All P1 and P2 user stories should now be fully functional

---

## Phase 6: User Story 4 - File and Tool Interaction (Priority: P3)

**Goal**: Handle Claude Code tool approvals and file viewing

**Independent Test**: Send command requiring tool approval, verify prompt appears with approve/reject options

### Tests for User Story 4 ⚠️ WRITE FIRST

- [ ] T102 [P] [US4] Contract test for tool_approval_request message in backend/tests/contract/test_websocket_protocol.py
- [ ] T103 [P] [US4] Integration test for tool approval flow in backend/tests/integration/test_tool_approvals.py
- [ ] T104 [P] [US4] Unit test for FileViewer component in frontend/tests/unit/components/FileViewer.spec.ts

### Backend Implementation for User Story 4

- [ ] T105 [US4] Implement tool approval request parsing from Claude stdout in backend/src/services/claude_bridge.py
- [ ] T106 [US4] Send tool_approval_request WebSocket message to client
- [ ] T107 [US4] Handle tool_approval response from client in WebSocket handler
- [ ] T108 [US4] Forward approval decision to Claude process stdin
- [ ] T109 [US4] Create GET /api/v1/files endpoint for file content retrieval (with path validation)

### Frontend Implementation for User Story 4

- [ ] T110 [P] [US4] Create ToolApprovalDialog.vue component in frontend/src/components/ToolApprovalDialog.vue
- [ ] T111 [P] [US4] Create FileViewer.vue component in frontend/src/components/FileViewer.vue
- [ ] T112 [US4] Update useWebSocket to handle tool_approval_request messages
- [ ] T113 [US4] Show ToolApprovalDialog when tool approval requested
- [ ] T114 [US4] Send tool_approval response via WebSocket
- [ ] T115 [US4] Add file path link detection in OutputDisplay.vue
- [ ] T116 [US4] Open FileViewer modal when file link clicked
- [ ] T117 [US4] Handle interactive prompt responses from Claude

**Checkpoint**: User Story 4 complete, full tool interaction supported

---

## Phase 7: User Story 5 - Multi-Device Access and Security (Priority: P3)

**Goal**: Secure authentication and multi-device session access

**Independent Test**: Login from one device, resume session from another device

### Tests for User Story 5 ⚠️ WRITE FIRST

- [X] T118 [P] [US5] Integration test for authentication flow in backend/tests/integration/test_authentication.py
- [X] T119 [P] [US5] Integration test for session authorization in backend/tests/integration/test_authorization.py
- [X] T120 [P] [US5] Unit test for auth store in frontend/tests/unit/stores/auth.spec.ts

### Backend Implementation for User Story 5

- [X] T121 [US5] Implement rate limiting middleware (10 commands/min per user)
- [X] T122 [US5] Add rate limit headers (X-RateLimit-*) to responses
- [X] T123 [US5] Implement session ownership validation in all endpoints
- [X] T124 [US5] Add security logging for failed auth attempts
- [X] T125 [US5] Create POST /api/v1/auth/logout endpoint
- [X] T126 [US5] Implement token refresh logic in authentication dependency

### Frontend Implementation for User Story 5

- [X] T127 [US5] Implement token refresh on 401 errors in API client
- [X] T128 [US5] Add session persistence with pinia-plugin-persistedstate
- [X] T129 [US5] Create SessionsView.vue for managing multiple sessions
- [ ] T130 [US5] Add responsive design for mobile/tablet in all components
- [X] T131 [US5] Implement logout functionality in App.vue
- [X] T132 [US5] Add "Resume Session" functionality in SessionsView.vue

**Checkpoint**: All user stories complete, full multi-device support

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T133 [P] Add comprehensive error messages with error codes in backend
- [ ] T134 [P] Implement user-friendly error display in frontend (Toast notifications)
- [ ] T135 [P] Add command cancellation support (cancel_command WebSocket message)
- [ ] T136 [P] Implement DELETE /api/v1/sessions/{id} endpoint
- [ ] T137 [P] Implement DELETE /api/v1/sessions/{id}/messages endpoint
- [ ] T138 [P] Add session title editing in SessionsView.vue
- [ ] T139 [P] Add copy-to-clipboard functionality for code blocks in OutputDisplay.vue
- [ ] T140 [P] Implement syntax highlighting for code blocks in OutputDisplay.vue
- [ ] T141 [P] Add markdown rendering for Claude responses
- [ ] T142 [P] Create README.md with setup instructions
- [ ] T143 [P] Add OpenAPI documentation generation in FastAPI
- [ ] T144 Run quickstart.md validation end-to-end
- [ ] T145 Performance optimization: Add database query indexes
- [ ] T146 Performance optimization: Implement frontend code splitting
- [ ] T147 Security audit: Review all input validation
- [ ] T148 Security audit: Review authentication flow
- [ ] T149 [P] Add Playwright E2E test for P1 user story
- [ ] T150 [P] Add Playwright E2E test for authentication flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on desired user stories being complete (minimum P1+P2 for MVP)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Security layer works with all stories

### Within Each User Story

- Tests (marked ⚠️) MUST be written and FAIL before implementation
- Backend models before services
- Backend services before API endpoints
- Backend API before frontend services
- Frontend services before components
- Frontend components before views
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T007, T009-T010)
- All Foundational phase tasks marked [P] can run in parallel within their subsections
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, tests marked [P] can run in parallel
- Within each user story, backend tasks marked [P] can run in parallel
- Within each user story, frontend tasks marked [P] can run in parallel
- Polish tasks marked [P] can all run in parallel

---

## Parallel Examples

### Phase 2: Foundational (Parallel Tasks)

```bash
# Backend models - all parallel
Task: T012, T013, T014, T015

# Pydantic schemas - all parallel
Task: T018, T019

# Frontend types - all parallel
Task: T033, T034, T035

# Frontend views - parallel
Task: T039, T040
```

### Phase 3: User Story 1 (Parallel Tasks)

```bash
# Tests - all parallel
Task: T043, T044, T045, T046, T047, T048

# Backend schemas - parallel
Task: T049, T050

# Frontend stores - parallel
Task: T061, T062, T063

# Frontend components - parallel
Task: T067, T068, T069
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T042) - CRITICAL
3. Complete Phase 3: User Story 1 (T043-T074)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

**Estimated MVP Task Count**: 74 tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T042)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T042)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (T043-T074)
   - **Developer B**: User Story 2 (T075-T086)
   - **Developer C**: User Story 5 authentication foundation (T118-T126)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD CRITICAL**: Verify tests fail before implementing (Red-Green-Refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

**Total Tasks**: 150
**MVP Tasks (P1 only)**: 74
**MVP + P2 Tasks**: 132
**Full Implementation**: 150

---

## Next Steps

1. **Start MVP**: Begin with T001 (Setup phase)
2. **TDD Discipline**: Write tests first for each user story
3. **Independent Testing**: Validate each story at checkpoints
4. **Incremental Delivery**: Ship P1, then P2, then P3

**Ready to begin implementation!** 🚀
