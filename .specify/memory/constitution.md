<!--
Sync Impact Report
==================
Version Change: Initial → 1.0.0
Added Principles:
  - I. Code Quality First
  - II. Test-Driven Development (NON-NEGOTIABLE)
  - III. User Experience Consistency
  - IV. Performance by Design
  - V. MVP & Simplicity
Added Sections:
  - Quality Standards
  - Development Workflow
Templates Status:
  ✅ plan-template.md - Constitution Check section aligns with quality gates
  ✅ spec-template.md - User scenarios and requirements structure supports UX consistency
  ✅ tasks-template.md - Task phases support MVP incremental delivery and testing discipline
  ⚠️ Command files - No updates needed (generic guidance only)
Follow-up TODOs: None
==================
-->

# Remote Vibe Coding Constitution

## Core Principles

### I. Code Quality First

**NON-NEGOTIABLE Requirements**:
- All code MUST pass linting and formatting checks before commit
- Functions and classes MUST have clear, descriptive names that reveal intent
- Public APIs MUST include documentation (docstrings/JSDoc/equivalent)
- Code complexity MUST be justified - default to simpler solutions
- Magic numbers and hard-coded values MUST be replaced with named constants
- Error messages MUST be specific, actionable, and user-friendly

**Rationale**: High code quality reduces maintenance burden, prevents bugs from entering
production, and enables team members to understand and modify code efficiently. Quality
gates catch issues early when they're cheapest to fix.

### II. Test-Driven Development (NON-NEGOTIABLE)

**Mandatory Testing Discipline**:
- Tests MUST be written BEFORE implementation (Red-Green-Refactor cycle)
- Every user story MUST have independently testable acceptance scenarios
- Tests MUST fail initially, proving they actually validate the functionality
- Test coverage MUST include: happy paths, edge cases, error conditions
- Integration tests MUST verify component interactions and contracts
- All tests MUST pass before code review and merge

**Rationale**: TDD ensures features are testable by design, provides living documentation,
catches regressions immediately, and gives confidence to refactor. Tests written after
implementation often miss edge cases and may not actually validate behavior.

### III. User Experience Consistency

**Consistency Requirements**:
- UI components MUST follow established design patterns within the project
- User interactions MUST behave predictably across all features
- Error messages and feedback MUST use consistent tone and terminology
- Loading states and transitions MUST provide clear user feedback
- Accessibility standards MUST be met (keyboard navigation, screen readers, contrast)
- User flows MUST be validated against acceptance scenarios in spec

**Rationale**: Consistent UX reduces cognitive load, improves user satisfaction, decreases
support requests, and builds trust. Inconsistent experiences feel unpolished and confuse
users, even if individual features work correctly.

### IV. Performance by Design

**Performance Standards**:
- Performance targets MUST be defined in plan.md for critical paths
- Database queries MUST be optimized (use indexes, avoid N+1 queries)
- API endpoints MUST respond within acceptable latency (define per endpoint)
- Frontend bundle sizes MUST be monitored and kept minimal
- Performance regressions MUST be caught in code review
- Profiling MUST be done for any suspected bottlenecks before optimization

**Rationale**: Performance is a feature. Slow systems frustrate users and limit scale.
Defining targets upfront prevents premature optimization while ensuring critical paths
meet user expectations. Performance issues are exponentially harder to fix later.

### V. MVP & Simplicity

**Simplicity Rules**:
- Features MUST start as MVP - deliver minimum viable functionality first
- User stories MUST be prioritized (P1, P2, P3...) and independently deliverable
- Each story MUST provide testable value without requiring other stories
- YAGNI principle MUST be followed - don't build what you don't need now
- Complexity MUST be justified in plan.md Complexity Tracking table
- Abstraction layers MUST be added only when needed (3+ concrete cases)

**Rationale**: MVP approach validates core value quickly, enables fast iteration based on
feedback, and avoids waste. Premature abstraction and over-engineering create maintenance
burden without benefit. Simple code is easier to understand, test, and change.

## Quality Standards

### Definition of Done

A feature is considered DONE only when:
1. All tests pass (unit, integration, and acceptance tests)
2. Code review approved by at least one team member
3. Documentation updated (docstrings, README, quickstart if applicable)
4. Performance meets defined targets for critical paths
5. No known blocking issues or unhandled edge cases
6. Accessibility requirements met for user-facing features

### Code Review Checklist

Reviewers MUST verify:
- Tests exist and cover the specified functionality
- Code follows project style and quality standards
- Error handling is present and appropriate
- User experience is consistent with existing features
- Performance implications considered
- Documentation is clear and sufficient
- Changes align with constitution principles

### Testing Standards

Test organization:
- **Contract Tests**: Validate API contracts and interfaces
- **Integration Tests**: Verify component interactions and data flow
- **Unit Tests**: Test individual functions and logic
- Tests MUST be independent (no shared state between tests)
- Tests MUST use mocks/stubs for external dependencies
- Test names MUST clearly describe what is being tested

## Development Workflow

### Feature Development Process

1. **Specification Phase**:
   - Create spec.md with prioritized user stories
   - Define acceptance scenarios for each story
   - Identify key entities and requirements

2. **Planning Phase**:
   - Create plan.md with technical approach
   - Run Constitution Check to verify compliance
   - Document complexity if violating simplicity principle
   - Define performance targets for critical paths

3. **Implementation Phase**:
   - Create tasks.md organized by user story priority
   - For each task:
     - Write failing tests first (Red)
     - Implement minimum code to pass (Green)
     - Refactor for quality (Refactor)
   - Commit after each logical unit of work

4. **Validation Phase**:
   - Verify all tests pass
   - Run quickstart.md to validate end-to-end
   - Check Definition of Done criteria
   - Request code review

### Branch and Commit Strategy

- Branch naming: `###-feature-name` (where ### is feature number)
- Commit messages MUST explain WHY, not just WHAT
- Commits MUST be atomic and focused on single concern
- All tests MUST pass before pushing

### Independent User Story Delivery

Each user story completion MUST enable:
- Independent deployment and demonstration
- Testing without requiring other incomplete stories
- Delivery of measurable user value
- Validation against acceptance criteria

## Governance

### Constitutional Authority

- This constitution is the supreme governing document for project development
- All decisions, code, and processes MUST comply with these principles
- Violations MUST be justified in plan.md Complexity Tracking table
- PRs violating principles without justification MUST be rejected

### Amendment Process

To amend this constitution:
1. Propose change with clear rationale
2. Assess impact on existing templates and features
3. Update all affected templates and documentation
4. Increment version:
   - **MAJOR**: Remove or redefine core principles (breaking change)
   - **MINOR**: Add new principle or section
   - **PATCH**: Clarify wording or fix non-semantic issues
5. Document change in Sync Impact Report

### Compliance Review

Constitution compliance MUST be verified at:
- Specification review (user stories testable?)
- Planning review (Constitution Check passed?)
- Code review (quality standards met?)
- Pre-merge (all tests pass, DoD met?)

### Complexity Justification

When violating simplicity principle, document in plan.md:
- **Violation**: What principle is being violated
- **Why Needed**: Specific problem requiring complexity
- **Simpler Alternative Rejected**: Why simpler approach insufficient

**Version**: 1.0.0 | **Ratified**: 2025-10-13 | **Last Amended**: 2025-10-13
