# /validate - Validation Command Template

**Purpose:** Execute comprehensive validation pyramid for feature/codebase

**Usage:**
```bash
/validate [scope] [level]
```

**Parameters:**
- `scope`: What to validate (feature name, file path, or "all")
- `level`: Validation depth (1-5, or "full" for all levels)

---

## COMMAND IMPLEMENTATION

```markdown
# File: .claude/commands/validate.md

---
description: Execute validation pyramid (syntax → types → tests → integration → review)
---

## VALIDATION SCOPE

Scope to validate: $1 (default: "all")
Validation level: $2 (default: "full")

**Available scopes:**
- `all` - Validate entire codebase
- `[feature-name]` - Validate specific feature (reads from plans/[feature-name].md)
- `[file-path]` - Validate specific file/directory

**Available levels:**
- `1` - Syntax & Formatting only
- `2` - Level 1 + Type Safety
- `3` - Level 1-2 + Unit Tests
- `4` - Level 1-3 + Integration Tests
- `5` or `full` - All levels + Manual Testing + Human Review

---

## LEVEL 1: SYNTAX & FORMATTING

### Backend (Python)

**Formatting:**
!black $1 --check
!ruff format $1 --check

**If formatting issues found:**
!black $1
!ruff format $1

**Linting:**
!ruff check $1

**Expected:** 0 errors, all files formatted.

**Status:** [ PASS / FAIL ]

---

### Frontend (TypeScript/JavaScript)

**Formatting:**
!npm run format:check

**If formatting issues found:**
!npm run format

**Linting:**
!npm run lint

**Expected:** 0 errors, all files formatted.

**Status:** [ PASS / FAIL ]

---

## LEVEL 2: TYPE SAFETY

### Backend (Python)

**Type Checking:**
!mypy $1 --strict

**Alternative (if mypy config exists):**
!mypy $1

**Expected:** 0 type errors.

**Common issues to check:**
- Missing type annotations on function parameters
- Missing return type annotations
- `Any` types (should be avoided in strict mode)
- Untyped third-party libraries (need type stubs)

**Status:** [ PASS / FAIL ]

---

### Frontend (TypeScript)

**Type Checking:**
!npm run typecheck

**Alternative:**
!tsc --noEmit

**Expected:** 0 type errors.

**Common issues to check:**
- Implicit `any` types
- Missing prop types in components
- Unsafe type assertions (`as any`)
- Untyped external libraries

**Status:** [ PASS / FAIL ]

---

## LEVEL 3: UNIT TESTS

### Backend (Python)

**Run Unit Tests:**
!pytest tests/ -v -m "not integration" --cov=$1 --cov-report=term-missing

**Expected:**
- All tests pass
- Coverage ≥ 80% (or project-defined threshold)

**Coverage Report Analysis:**
- Lines covered: [X / Y] ([Z%])
- Branches covered: [X / Y] ([Z%])
- Files with < 80% coverage: [List files]

**Action if coverage < threshold:**
- Identify untested code paths
- Add missing tests before proceeding

**Status:** [ PASS / FAIL ]
**Coverage:** [ X% ]

---

### Frontend (TypeScript/JavaScript)

**Run Unit Tests:**
!npm run test:unit

**Alternative (with coverage):**
!npm run test:coverage

**Expected:**
- All tests pass
- Coverage ≥ 80% (or project-defined threshold)

**Coverage Report Analysis:**
- Statements: [X%]
- Branches: [X%]
- Functions: [X%]
- Lines: [X%]

**Status:** [ PASS / FAIL ]
**Coverage:** [ X% ]

---

## LEVEL 4: INTEGRATION TESTS

### Backend (Python)

**Run Integration Tests:**
!pytest tests/ -v -m integration

**Alternative (run all tests):**
!pytest tests/ -v

**Expected:**
- All tests pass
- No flaky tests (re-run if failures to confirm)

**Check for:**
- Database connection issues
- External API failures (mocks working?)
- Race conditions (tests passing inconsistently)

**Status:** [ PASS / FAIL ]

---

### Frontend (TypeScript/JavaScript)

**Run Integration Tests:**
!npm run test:integration

**Alternative (E2E tests if configured):**
!npm run test:e2e

**Expected:**
- All tests pass
- No timeouts or flaky tests

**Check for:**
- API mocking working correctly
- Component integration (parent + child communication)
- Routing working

**Status:** [ PASS / FAIL ]

---

### Full Stack Integration

**If both backend + frontend:**

**Step 1: Start backend**
!uvicorn app.main:app --reload &

**Step 2: Start frontend**
!npm run dev &

**Step 3: Run E2E tests**
!npm run test:e2e -- --headed=false

**Expected:**
- Full user journeys work end-to-end
- API contracts match (frontend requests work with backend responses)

**Status:** [ PASS / FAIL ]

---

## LEVEL 5: MANUAL TESTING & HUMAN REVIEW

### Manual Testing

**If backend API:**

**Test critical endpoints:**
```bash
# Example: Health check
!curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Example: User login
!curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# Expected: {"access_token":"...", "token_type":"bearer"}

# Add feature-specific manual tests here
!curl [HTTP_METHOD] [http://localhost:PORT/api/v1/endpoint] [options]
# Expected: [Describe expected response]
```

**Manual Test Checklist:**
- [ ] Happy path works (valid inputs → expected outputs)
- [ ] Error handling works (invalid inputs → appropriate errors)
- [ ] Edge cases handled (empty data, boundary values)
- [ ] Performance acceptable (response time < X ms)

**Status:** [ PASS / FAIL ]

---

**If frontend:**

**Open in browser:**
1. Navigate to: http://localhost:[PORT]
2. Test user flow:
   - [ ] [Step 1 - e.g., "Click login button"]
   - [ ] [Step 2 - e.g., "Enter credentials"]
   - [ ] [Step 3 - e.g., "Submit form"]
   - [ ] [Expected: "Success message appears, redirected to dashboard"]

**Visual/UX Checks:**
- [ ] UI renders correctly (no layout breaks)
- [ ] Loading states display appropriately
- [ ] Error messages are user-friendly
- [ ] Responsive design works (test on mobile viewport)
- [ ] Accessibility (keyboard navigation, screen reader friendly)

**Status:** [ PASS / FAIL ]

---

### Code Review (Human or AI)

**Read code and check for:**

**1. Code Quality:**
- [ ] Functions are single-purpose (SRP)
- [ ] Code is DRY (no unnecessary duplication)
- [ ] Naming is clear and descriptive
- [ ] Complex logic has comments explaining "why"

**2. Security:**
- [ ] No hardcoded secrets (API keys, passwords)
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (using parameterized queries)
- [ ] XSS prevention (sanitized outputs)
- [ ] CSRF protection (if applicable)

**3. Performance:**
- [ ] No N+1 queries (database)
- [ ] Appropriate indexes on frequently queried fields
- [ ] No unnecessary API calls (frontend)
- [ ] Large lists virtualized/paginated

**4. Error Handling:**
- [ ] All exceptions caught and handled appropriately
- [ ] User-friendly error messages
- [ ] Errors logged for debugging
- [ ] No silent failures

**5. Testing:**
- [ ] Tests cover happy path
- [ ] Tests cover error cases
- [ ] Tests cover edge cases
- [ ] No tests checking implementation details (test behavior, not internals)

**Status:** [ PASS / FAIL ]

---

## VALIDATION REPORT

**Feature/Scope Validated:** $1
**Validation Level:** $2
**Executed:** [DATE & TIME]

---

### Summary

| Level | Status | Details |
|-------|--------|---------|
| 1. Syntax & Formatting | [✅ PASS / ❌ FAIL] | [Brief note] |
| 2. Type Safety | [✅ PASS / ❌ FAIL] | [Brief note] |
| 3. Unit Tests | [✅ PASS / ❌ FAIL] | Coverage: [X%] |
| 4. Integration Tests | [✅ PASS / ❌ FAIL] | [Brief note] |
| 5. Manual & Review | [✅ PASS / ❌ FAIL] | [Brief note] |

**Overall Status:** [✅ ALL PASS / ⚠️ PARTIAL PASS / ❌ FAIL]

---

### Failures Detected

**If any level failed, list issues here:**

**Level 1 Issues:**
- [Issue 1 - e.g., "app/api/users.py:45 - Line too long (120 > 88 chars)"]
- [Issue 2]

**Level 2 Issues:**
- [Issue 1 - e.g., "app/services/auth.py:12 - Missing return type annotation"]
- [Issue 2]

**Level 3 Issues:**
- [Issue 1 - e.g., "tests/test_products.py::test_create_product FAILED"]
- [Issue 2]

**Level 4 Issues:**
- [Issue 1 - e.g., "Integration test timeout after 30s"]

**Level 5 Issues:**
- [Issue 1 - e.g., "Manual test: Login fails with valid credentials"]
- [Issue 2 - e.g., "Code review: Hardcoded API key found in config.py"]

---

### Actions Required

**To fix failures:**

**Priority 1 (Blockers - must fix before merging):**
1. [Action - e.g., "Fix type error in app/services/auth.py:12"]
2. [Action]

**Priority 2 (Important - fix before deploying):**
1. [Action - e.g., "Add tests for edge case in test_products.py"]

**Priority 3 (Nice-to-have - can address later):**
1. [Action - e.g., "Refactor function X for better readability"]

---

## REVALIDATION

**After fixes applied:**

!/ validate $1 $2

**Expected:** All levels pass.

**If still failing:**
- Investigate root cause
- Do NOT proceed until validation passes
- Update plan if approach needs to change

---

## DEFINITION OF DONE

This feature/code is **VALIDATED** and ready to merge when:

- [ ] All 5 validation levels pass
- [ ] No P1 issues remaining (P2/P3 can be tracked as tech debt)
- [ ] Code reviewed and approved
- [ ] Documentation updated (if needed)
- [ ] Changelog updated (if user-facing change)

**Sign-off:** [Your name / AI Agent]
**Date:** [DATE]

---

## NOTES

**Validation process notes:**
- [Note 1 - e.g., "Level 3 took longer due to slow database tests, consider mocking"]
- [Note 2]

**Improvements for next time:**
- [Improvement 1 - e.g., "Add pre-commit hooks to catch Level 1 issues earlier"]

---

```

---

## CUSTOMIZATION GUIDE

### For Your Project

**1. Adjust Coverage Thresholds:**

Replace `80%` with your project's standard:
```markdown
**Expected:**
- Coverage ≥ [YOUR_THRESHOLD]%
```

---

**2. Add Project-Specific Checks:**

Example for Django projects:
```markdown
## LEVEL 2.5: DJANGO CHECKS

**Run Django system checks:**
!python manage.py check --deploy

**Expected:** No errors or warnings.

**Status:** [ PASS / FAIL ]
```

Example for projects with database migrations:
```markdown
## LEVEL 3.5: MIGRATION CHECKS

**Check for pending migrations:**
!python manage.py makemigrations --check --dry-run

**Expected:** No pending migrations.

**Status:** [ PASS / FAIL ]
```

---

**3. Customize Manual Tests:**

Replace generic curl examples with your actual endpoints:
```markdown
# Test user registration
!curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@example.com","password":"SecurePass123!"}'
# Expected: {"id":1,"email":"newuser@example.com","created_at":"2025-..."}
```

---

**4. Add Security Scans:**

If you have security tools:
```markdown
## LEVEL 4.5: SECURITY SCAN

**Run security checks:**
!bandit -r app/  # Python
!npm audit  # JavaScript

**Expected:** 0 high/critical vulnerabilities.

**Status:** [ PASS / FAIL ]
```

---

**5. Environment-Specific Validation:**

For different environments:
```markdown
## VALIDATION ENVIRONMENT

**Environment:** $3 (default: "local")

**If environment == "staging":**
- Use staging database
- Test with staging API keys
- Validate deployment config

**If environment == "production":**
- Read-only validation (no destructive tests)
- Validate monitoring/alerting working
- Check production secrets configured
```

---

## INTEGRATION WITH PIV LOOP

### Usage in PIV Loop

**After Implementation Phase:**

```bash
# Plan
/plan "Add user search endpoint"

# Implement
/execute plans/user-search.md

# Validate ← YOU ARE HERE
/validate user-search full

# If validation passes:
- Mark feature as complete
- Create PR / merge to main

# If validation fails:
- Review failures
- Fix issues
- Re-run /validate
- Iterate until passes
```

---

### Automated Validation (CI/CD)

**In GitHub Actions / GitLab CI:**

```yaml
# .github/workflows/validate.yml

name: Validation Pyramid

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Level 1 - Syntax & Formatting
        run: |
          black . --check
          ruff check .

      - name: Level 2 - Type Safety
        run: mypy app/ --strict

      - name: Level 3 - Unit Tests
        run: pytest tests/ -m "not integration" --cov=app --cov-fail-under=80

      - name: Level 4 - Integration Tests
        run: pytest tests/ -m integration

      # Level 5 (manual) is not automated
```

---

## EXAMPLES

### Example 1: Validate Specific Feature

```bash
/validate user-authentication full
```

**Output:**
```
✅ Level 1: Syntax & Formatting - PASS
✅ Level 2: Type Safety - PASS
✅ Level 3: Unit Tests - PASS (Coverage: 92%)
✅ Level 4: Integration Tests - PASS
⚠️ Level 5: Manual Testing - PARTIAL PASS
   - Issue: Password reset email not sent (SMTP not configured)

Overall: ⚠️ PARTIAL PASS

Action Required:
- Configure SMTP settings for password reset emails
- Re-validate after fix
```

---

### Example 2: Validate Entire Codebase

```bash
/validate all 3
```

**Output:**
```
Running Levels 1-3 on entire codebase...

✅ Level 1: Syntax & Formatting - PASS
❌ Level 2: Type Safety - FAIL
   - app/services/products.py:45 - Missing return type
   - app/api/users.py:12 - Parameter 'user_id' has implicit type 'Any'

Skipping Level 3 (Level 2 must pass first)

Overall: ❌ FAIL

Fix type errors before proceeding.
```

---

### Example 3: Quick Validation (Level 1-2 Only)

```bash
/validate src/components/ProductCard.tsx 2
```

**Output:**
```
✅ Level 1: Syntax & Formatting - PASS
✅ Level 2: Type Safety - PASS

Overall: ✅ PASS

Component is ready for further testing.
```

---

## BEST PRACTICES

### 1. Validate Early, Validate Often

Don't wait until feature is "done" to validate.

**Good workflow:**
- After each task in plan → Run Level 1-2 (quick checks)
- After completing service layer → Run Level 3 (unit tests)
- After completing API layer → Run Level 4 (integration tests)
- After everything → Run Level 5 (manual + review)

**Benefit:** Catch issues early when they're easier to fix.

---

### 2. Don't Skip Levels

❌ **Bad:** "Tests pass, so I'll skip type checking"
✅ **Good:** Run all levels in order

**Why:** Each level catches different types of issues. Skipping levels means hidden bugs.

---

### 3. Treat Validation Failures as Blockers

❌ **Bad:** "Validation failed but I'll merge anyway, we'll fix later"
✅ **Good:** "Validation failed, must fix before proceeding"

**Why:** "Fix later" = technical debt that compounds.

---

### 4. Automate What You Can

- Level 1-4 → Automate in CI/CD
- Level 5 → Requires human judgment, can't fully automate

**Benefit:** Validation happens automatically on every commit.

---

### 5. Document Validation Results

Save validation reports for future reference:

```bash
/validate my-feature full > validation-reports/my-feature-2025-01-18.md
```

**Benefit:** Track quality over time, identify patterns.

---

## TROUBLESHOOTING

### Issue: "Command not found"

**Cause:** Tool not installed or not in PATH

**Fix:**
```bash
# Python tools
!pip install black ruff mypy pytest pytest-cov

# Node tools
!npm install --save-dev prettier eslint typescript vitest
```

---

### Issue: "Tests pass locally but fail in CI"

**Cause:** Environment differences

**Fix:**
- Check Python/Node versions match
- Check dependencies installed in CI
- Check environment variables set
- Check database/external services available

---

### Issue: "Validation takes too long"

**Cause:** Too many tests or slow tests

**Fix:**
- Run subset of tests: `pytest tests/test_feature.py` instead of all tests
- Parallelize tests: `pytest -n auto` (requires pytest-xdist)
- Mock slow external calls
- Use in-memory database for tests

---

## REFERENCES

**Related Files:**
- `plan-template.md` - Plans include validation commands
- `code-review.md` - Human code review checklist (Level 5)
- `CLAUDE.md` - Project standards (what validation checks against)

**External:**
- Pytest: https://docs.pytest.org/
- Mypy: https://mypy.readthedocs.io/
- Vitest: https://vitest.dev/
- Testing Best Practices: https://testingjavascript.com/

---

**🎯 Remember: Validation is not optional. It's the "V" in PIV Loop.**

**Code without validation is hope, not certainty. 🚀**
