# Plan Template - [FEATURE NAME]

**Created:** [DATE]
**Author:** [YOUR NAME / AI Agent]
**Status:** [Draft / In Progress / Completed]

---

## CONTEXT REFERENCES

**Project Standards:**
- Read: CLAUDE.md (project-wide standards and patterns)

**Existing Code:**
- Read: [path/to/similar_implementation.py] ([Why - what pattern to follow])
- Read: [path/to/model.py] ([Why - understand data structures])
- Read: [path/to/test.py] ([Why - understand testing patterns])

**Patterns to Follow:**
- Pattern: [Description of pattern] from [file.py:line-range]
- Example: "Follow error handling pattern from app/api/products.py:25-30"

**External Documentation:**
- Docs: [URL to relevant documentation]
- Reference: [Path to internal docs]

**Exploration Needed:**
- Explore: [directory/] ([What to understand - e.g., "component structure"])

---

## IMPLEMENTATION PLAN

### Feature Overview

**Feature:** [Feature name in 3-5 words]

**Problem:**
[What problem does this feature solve? Be specific about user pain point or business need.]

**Solution:**
[High-level approach to solving the problem. Explain the "what" not the "how".]

**User Story:**
As a [user type], I want to [action], so that [benefit].

**Acceptance Criteria:**
1. [ ] [Specific, testable criterion]
2. [ ] [Specific, testable criterion]
3. [ ] [Specific, testable criterion]

---

### Technical Architecture

**Components to Build:**

**Backend:**
- **Models:** [List models - e.g., "Product, ProductVariant"]
  - [Model1]: [Purpose, key fields]
  - [Model2]: [Purpose, key fields]

- **Services:** [List service layer functions]
  - [service_function_1]: [Purpose, inputs → output]
  - [service_function_2]: [Purpose, inputs → output]

- **Endpoints:** [List API endpoints]
  - [HTTP_METHOD] [/api/v1/path]: [Purpose, request/response]
  - Example: "GET /api/v1/products/search: Search products by query"

- **Middleware:** [If applicable]
  - [middleware_name]: [Purpose]

**Frontend:**
- **Pages:** [List pages/routes]
  - [PageName] ([/route]): [Purpose]

- **Components:** [List UI components]
  - [ComponentName]: [Purpose, props]

- **State Management:** [How data flows]
  - [State change needed]

- **API Integration:** [How frontend calls backend]
  - [API client function]: [Endpoint it calls]

**Database:**
- **Migrations:** [If schema changes needed]
  - [Migration description]

- **Indexes:** [If performance optimization needed]
  - [Index on which fields]

**Infrastructure:**
- **Environment Variables:** [If new config needed]
  - [ENV_VAR_NAME]: [Purpose, default value]

- **External Services:** [If integrating third-party]
  - [Service name]: [What it does, API used]

---

### Technical Decisions

**Decision 1:** [Technology/approach chosen]
- **Rationale:** [Why this choice]
- **Alternatives considered:** [What else was considered]
- **Trade-offs:** [What we're sacrificing, what we're gaining]

**Decision 2:** [Technology/approach chosen]
- **Rationale:** [Why this choice]
- **Alternatives considered:** [What else was considered]
- **Trade-offs:** [What we're sacrificing, what we're gaining]

---

### Edge Cases & Error Handling

**Edge Case 1:** [Scenario]
- **Handling:** [How to handle it]
- **Error response:** [What user sees - status code, message]

**Edge Case 2:** [Scenario]
- **Handling:** [How to handle it]
- **Error response:** [What user sees]

**Validation Rules:**
- [Field/input]: [Validation rule - e.g., "email must be valid format"]
- [Field/input]: [Validation rule]

---

### Security Considerations

- **Authentication:** [Required? Which endpoints?]
- **Authorization:** [Permission checks needed?]
- **Input Validation:** [How to prevent injection attacks]
- **Rate Limiting:** [If applicable - which endpoints, what limits]
- **Data Sanitization:** [What data needs sanitization]

---

## STEP-BY-STEP TASKS

### Phase 1: Data Layer

**Task 1.1: Create Data Models**
- File: [path/to/models.py]
- Models to create:
  - `[ModelName]`:
    - Fields: [field1: type, field2: type, ...]
    - Relationships: [relationship to other models]
    - Constraints: [unique, nullable, etc.]

**Task 1.2: Database Migration**
- Create migration: `![migration command]`
- Migration file: [path/to/migration.py]
- Changes:
  - [Change 1 - e.g., "Add users table"]
  - [Change 2]
- Rollback strategy: [How to undo migration]

**Task 1.3: Seed Data** (if applicable)
- File: [path/to/seed.py]
- Seed: [What data to seed - e.g., "default roles, sample products"]

---

### Phase 2: Business Logic

**Task 2.1: Create Service Layer**
- File: [path/to/service.py]
- Functions to implement:
  - `[function_name](params: types) -> return_type`:
    - Purpose: [What it does]
    - Logic: [High-level steps]
    - Error handling: [What exceptions to raise]

**Task 2.2: Add Validation Logic**
- File: [path/to/validators.py] (if separate)
- Validations:
  - [validation_1]: [Rule]
  - [validation_2]: [Rule]

---

### Phase 3: API Layer

**Task 3.1: Create API Endpoint(s)**
- File: [path/to/api.py]
- Endpoint: [HTTP_METHOD] [/api/v1/path]
  - Request:
    - Body: [RequestModel with fields]
    - Query params: [param1: type, param2: type]
    - Headers: [if special headers needed]
  - Response:
    - Success ([status_code]): [ResponseModel with fields]
    - Error ([status_code]): [ErrorModel with fields]
  - Logic flow:
    1. [Step 1 - e.g., "Validate request body"]
    2. [Step 2 - e.g., "Call service layer"]
    3. [Step 3 - e.g., "Return response"]

**Task 3.2: Add Middleware** (if applicable)
- File: [path/to/middleware.py]
- Middleware: [middleware_name]
  - Purpose: [What it does - e.g., "verify JWT token"]
  - Apply to: [Which endpoints]

---

### Phase 4: Frontend (if applicable)

**Task 4.1: Create API Client**
- File: [path/to/api-client.ts]
- Functions:
  - `[functionName](params) -> Promise<Response>`:
    - Endpoint: [HTTP_METHOD] [/api/v1/path]
    - Error handling: [How to handle errors]

**Task 4.2: Create Components**
- Component: [ComponentName]
  - File: [path/to/Component.tsx]
  - Props: [prop1: type, prop2: type]
  - State: [state1: type, state2: type]
  - Rendering: [What it displays]
  - Events: [What user interactions it handles]

**Task 4.3: Create Page** (if new page)
- File: [path/to/Page.tsx]
- Route: [/route-path]
- Layout: [Description of page sections]
- Data fetching: [When/how data is loaded]

**Task 4.4: Update Routing** (if new route)
- File: [path/to/App.tsx]
- Add route: [/route-path] → [PageComponent]
- Protected: [Yes/No - requires auth]

---

### Phase 5: Testing

**Task 5.1: Unit Tests - Backend**
- File: [path/to/test_service.py]
- Tests to write:
  - `test_[function]_success()`: Happy path
  - `test_[function]_invalid_input()`: Validation error
  - `test_[function]_edge_case()`: Edge case handling
  - `test_[function]_error()`: Error handling

**Task 5.2: Integration Tests - Backend**
- File: [path/to/test_api.py]
- Tests to write:
  - `test_[endpoint]_success()`: Full request → response flow
  - `test_[endpoint]_unauthorized()`: Without auth (if protected)
  - `test_[endpoint]_validation_error()`: Invalid request body
  - `test_[endpoint]_not_found()`: Resource doesn't exist

**Task 5.3: Component Tests - Frontend** (if applicable)
- File: [path/to/Component.test.tsx]
- Tests to write:
  - `test_renders_correctly()`: Component renders with props
  - `test_handles_loading()`: Loading state displays
  - `test_handles_error()`: Error state displays
  - `test_user_interaction()`: User clicks button, state updates

**Task 5.4: E2E Tests** (if critical flow)
- File: [path/to/feature.spec.ts]
- User journey to test:
  1. [Step 1 - e.g., "User opens page"]
  2. [Step 2 - e.g., "User fills form"]
  3. [Step 3 - e.g., "User submits"]
  4. [Step 4 - e.g., "Success message appears"]

---

### Phase 6: Documentation & Cleanup

**Task 6.1: Add Docstrings**
- Files: [All new Python files]
- Add:
  - Module docstring (what the module does)
  - Function docstrings (params, returns, raises)

**Task 6.2: Update API Documentation**
- File: [path/to/openapi.yaml] or auto-generated
- Document: [New endpoints with request/response schemas]

**Task 6.3: Update README** (if user-facing change)
- File: README.md
- Add: [Section about new feature, how to use it]

**Task 6.4: Code Cleanup**
- Remove: [Any debug prints, commented code, TODOs]
- Format: Run [formatter - e.g., "black app/"]
- Lint: Run [linter - e.g., "ruff check app/"]

---

## VALIDATION COMMANDS

### Level 1: Syntax & Formatting

```bash
# Python formatting (if backend)
!black [path/to/files/]
!ruff check [path/to/files/]

# TypeScript formatting (if frontend)
!npm run format
!npm run lint
```

**Expected:** No errors, files formatted correctly.

---

### Level 2: Type Safety

```bash
# Python type checking (if backend)
!mypy [path/to/file.py] --strict

# TypeScript type checking (if frontend)
!npm run typecheck
```

**Expected:** 0 type errors.

---

### Level 3: Unit Tests

```bash
# Backend unit tests
!pytest tests/test_[module].py -v --cov=[module]

# Frontend component tests
!npm run test -- [Component].test.tsx
```

**Expected:** All tests pass, coverage > 80%.

---

### Level 4: Integration Tests

```bash
# Backend integration tests
!pytest tests/test_[api].py -v -m integration

# Full backend test suite
!pytest tests/ -v
```

**Expected:** All tests pass.

---

### Level 5: Manual Testing

```bash
# Start backend server (if applicable)
!uvicorn app.main:app --reload &

# Start frontend server (if applicable)
!npm run dev &

# Test endpoint manually
![HTTP_METHOD] [http://localhost:PORT/api/v1/path] [options]
# Example: curl -X POST http://localhost:8000/api/v1/products -d '{"name":"Test"}'
```

**Expected Output:**
```json
{
  "expected": "response structure here"
}
```

**Manual UI Testing Steps:**
1. [Step 1 - e.g., "Open http://localhost:3000/products"]
2. [Step 2 - e.g., "Click 'Add Product' button"]
3. [Step 3 - e.g., "Fill form and submit"]
4. [Expected: "Success message appears, product added to list"]

---

### Level 6: Build & Deploy

```bash
# Backend build check
!python -m compileall app/

# Frontend build
!npm run build
```

**Expected:** Build succeeds with no errors.

---

## DEFINITION OF DONE

This feature is considered **DONE** when:

**Functionality:**
- [ ] All acceptance criteria met
- [ ] All tasks in STEP-BY-STEP section completed
- [ ] All edge cases handled appropriately

**Quality:**
- [ ] All validation commands pass (Levels 1-6)
- [ ] Test coverage ≥ 80% (unit + integration)
- [ ] No linting/type errors
- [ ] Code reviewed (if team process requires)

**Documentation:**
- [ ] Code has docstrings/comments where needed
- [ ] API documentation updated (if endpoints changed)
- [ ] README updated (if user-facing change)

**Deployment:**
- [ ] Tested in staging environment
- [ ] Database migrations tested (up + down)
- [ ] Feature flag added (if large/risky feature)
- [ ] Monitoring/logging added for critical paths

**Sign-off:**
- [ ] Product Owner approves functionality
- [ ] QA approves (if QA process exists)
- [ ] Stakeholders notified of deployment

---

## ROLLBACK PLAN

**If this feature causes issues in production:**

**Step 1: Immediate Mitigation**
- [ ] [Action - e.g., "Set feature flag FEATURE_ENABLED=false"]
- Expected: [What happens - e.g., "Feature disabled, users see old flow"]

**Step 2: Database Rollback** (if migration applied)
- [ ] Run: `![rollback command - e.g., "alembic downgrade -1"]`
- Expected: [What happens - e.g., "New tables dropped, old schema restored"]

**Step 3: Code Rollback**
- [ ] Git: `!git revert [commit_hash]`
- [ ] Deploy: [Deployment command]
- Expected: [What happens]

**Data Loss Risk:** [Yes/No - describe what data might be lost on rollback]

**Estimated Rollback Time:** [X minutes]

---

## RISKS & MITIGATIONS

**Risk 1:** [Description of risk]
- **Probability:** [Low / Medium / High]
- **Impact:** [Low / Medium / High]
- **Mitigation:** [How to prevent/reduce this risk]
- **Contingency:** [What to do if risk materializes]

**Risk 2:** [Description of risk]
- **Probability:** [Low / Medium / High]
- **Impact:** [Low / Medium / High]
- **Mitigation:** [How to prevent/reduce this risk]
- **Contingency:** [What to do if risk materializes]

---

## NOTES & LEARNINGS

**Implementation Notes:**
- [Note 1 - discoveries during implementation]
- [Note 2 - things that worked well]
- [Note 3 - things that didn't work, had to change approach]

**Blockers Encountered:**
- [Blocker 1 - what blocked progress, how resolved]

**Future Improvements:**
- [Improvement 1 - what could be done better in future]
- [Improvement 2 - technical debt incurred, plan to address]

**Lessons Learned:**
- [Lesson 1 - what you learned from this feature]

---

## RELATED LINKS

- **GitHub Issue:** [Link to issue/ticket]
- **Design Doc:** [Link to design doc if applicable]
- **Figma/Mockups:** [Link to UI designs if applicable]
- **API Documentation:** [Link to API docs]
- **Deployment:** [Link to deployment pipeline/logs]

---

## CHANGELOG

**[DATE]** - [Author]
- Created initial plan

**[DATE]** - [Author]
- Updated [section] based on [reason]

**[DATE]** - [Author]
- Feature completed, plan archived

---

## TEMPLATE USAGE INSTRUCTIONS

**How to use this template:**

1. **Copy this template** to `plans/[feature-name].md`

2. **Fill all [BRACKETED] placeholders** with specific information

3. **Delete sections that don't apply** (e.g., if no frontend, delete Phase 4)

4. **Customize for your project**:
   - Add project-specific sections (e.g., "Event Sourcing Considerations")
   - Remove sections not relevant (e.g., "Rollback Plan" for low-risk features)

5. **Keep it updated** as implementation progresses:
   - Check off tasks as completed
   - Add notes/learnings in real-time
   - Update risks if new ones discovered

6. **Use with /execute command**:
   - `/execute` reads this plan
   - Implements step-by-step
   - Validates at each level

7. **Reference in commits**:
   - `git commit -m "Implement [feature] - Phase 3 complete (see plans/feature.md)"`

**This template ensures:**
- ✅ Consistent planning across all features
- ✅ Nothing forgotten (context, tests, validation, rollback)
- ✅ Executable by AI (structured, unambiguous)
- ✅ Documentación for future reference

**Pro tip:** Save common customizations of this template for recurring feature types (e.g., `plan-template-api-endpoint.md`, `plan-template-ui-component.md`)
