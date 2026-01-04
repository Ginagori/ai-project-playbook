# /code-review - Code Review Command Template

**Purpose:** Perform systematic code review (human or AI-assisted)

**Usage:**
```bash
/code-review [scope] [focus]
```

**Parameters:**
- `scope`: What to review (file path, feature name, PR number, or "all")
- `focus`: Review focus (security, performance, quality, or "full")

---

## COMMAND IMPLEMENTATION

```markdown
# File: .claude/commands/code-review.md

---
description: Systematic code review for quality, security, and best practices
---

## REVIEW SCOPE

Code to review: $1 (default: "recent changes")
Review focus: $2 (default: "full")

**Available scopes:**
- `[file-path]` - Review specific file or directory
- `[feature-name]` - Review feature (reads from plans/[feature-name].md)
- `PR-[number]` - Review pull request
- `latest` - Review latest commit
- `all` - Review entire codebase (use sparingly)

**Available focus areas:**
- `security` - Security vulnerabilities only
- `performance` - Performance issues only
- `quality` - Code quality and maintainability only
- `full` - All of the above (comprehensive review)

---

## PRE-REVIEW CHECKLIST

**Before starting review, verify:**

- [ ] Code compiles/builds successfully
- [ ] All tests pass
- [ ] No linting/formatting errors
- [ ] Type checking passes

**If any above fail:**
→ Fix those first, then return for review

**Validation quick check:**
!/validate $1 2  # Run Level 1-2 validation

---

## REVIEW CATEGORIES

### 1. CODE QUALITY

#### 1.1 Readability

**Check for:**
- [ ] Function/variable names are descriptive (not `x`, `temp`, `data`)
- [ ] Functions are reasonably sized (< 50 lines ideally)
- [ ] Complex logic has explanatory comments
- [ ] Code follows consistent style (matches CLAUDE.md)

**Examples of issues:**

❌ **Bad:**
```python
def f(x, y):
    return x + y if x > 0 else y  # What does this do?
```

✅ **Good:**
```python
def calculate_total_price(base_price: float, tax: float) -> float:
    """Calculate total price including tax, only if base price is positive."""
    return base_price + tax if base_price > 0 else tax
```

**Review Notes:**
- [File]: [Line]: [Issue description]

---

#### 1.2 Single Responsibility Principle (SRP)

**Check for:**
- [ ] Functions do ONE thing
- [ ] Classes have ONE reason to change
- [ ] Modules group related functionality

**Examples of violations:**

❌ **Bad:**
```python
def handle_user_registration(email, password):
    # Validates email
    if "@" not in email:
        raise ValueError("Invalid email")

    # Hashes password
    hashed = bcrypt.hash(password)

    # Saves to database
    db.save(User(email=email, password=hashed))

    # Sends email
    send_email(email, "Welcome!")

    # Logs analytics
    analytics.track("user_registered")
```

✅ **Good:**
```python
def register_user(email: str, password: str) -> User:
    """Register new user (orchestration only)."""
    validate_email(email)
    hashed_password = hash_password(password)
    user = save_user(email, hashed_password)
    send_welcome_email(user)
    track_registration(user)
    return user
```

**Review Notes:**
- [File]: [Line]: [Function does too much - suggest splitting]

---

#### 1.3 DRY (Don't Repeat Yourself)

**Check for:**
- [ ] No copy-pasted code blocks
- [ ] Repeated logic extracted to functions
- [ ] Magic numbers/strings defined as constants

**Examples of violations:**

❌ **Bad:**
```python
# In file A
if user.role == "admin" or user.role == "superadmin":
    # do something

# In file B
if user.role == "admin" or user.role == "superadmin":
    # do something else
```

✅ **Good:**
```python
# In user.py
def is_admin(user: User) -> bool:
    return user.role in ["admin", "superadmin"]

# In file A
if is_admin(user):
    # do something

# In file B
if is_admin(user):
    # do something else
```

**Review Notes:**
- [Files with duplication]: [Suggest extraction to shared function]

---

#### 1.4 Error Handling

**Check for:**
- [ ] Exceptions caught appropriately (not bare `except:`)
- [ ] Errors logged with context
- [ ] User-friendly error messages
- [ ] No silent failures

**Examples of issues:**

❌ **Bad:**
```python
try:
    result = external_api.call()
except:  # Catches everything, even KeyboardInterrupt!
    pass  # Silent failure
```

✅ **Good:**
```python
try:
    result = external_api.call()
except ExternalAPIError as e:
    logger.error(f"External API call failed: {e}", exc_info=True)
    raise ServiceUnavailableError("Unable to process request at this time")
```

**Review Notes:**
- [File]: [Line]: [Improve error handling]

---

### 2. SECURITY

#### 2.1 Input Validation

**Check for:**
- [ ] All user inputs validated
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized outputs)
- [ ] Path traversal prevention (validate file paths)

**Examples of vulnerabilities:**

❌ **Bad (SQL Injection):**
```python
query = f"SELECT * FROM users WHERE email = '{email}'"  # Dangerous!
db.execute(query)
```

✅ **Good:**
```python
query = "SELECT * FROM users WHERE email = ?"
db.execute(query, (email,))  # Parameterized
```

❌ **Bad (XSS):**
```javascript
div.innerHTML = userInput;  // Dangerous if userInput contains <script>
```

✅ **Good:**
```javascript
div.textContent = userInput;  // Safe, text only
// Or use a sanitization library
div.innerHTML = DOMPurify.sanitize(userInput);
```

**Review Notes:**
- [File]: [Line]: [Security vulnerability - [type]]

---

#### 2.2 Authentication & Authorization

**Check for:**
- [ ] Protected endpoints require authentication
- [ ] Authorization checks before sensitive operations
- [ ] No hardcoded credentials
- [ ] Passwords hashed (not plain text)
- [ ] Tokens/sessions have expiration

**Examples of issues:**

❌ **Bad:**
```python
@app.get("/admin/users")
def get_all_users():
    return db.query(User).all()  # No auth check!
```

✅ **Good:**
```python
@app.get("/admin/users")
def get_all_users(current_user: User = Depends(get_current_admin_user)):
    # Requires admin authentication
    return db.query(User).all()
```

**Review Notes:**
- [File]: [Line]: [Missing auth/authorization check]

---

#### 2.3 Secrets Management

**Check for:**
- [ ] No API keys in code
- [ ] No passwords in code
- [ ] Secrets loaded from environment variables
- [ ] `.env` files in `.gitignore`

**Examples of issues:**

❌ **Bad:**
```python
API_KEY = "sk-1234567890abcdef"  # Hardcoded!
```

✅ **Good:**
```python
import os
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

**Review Notes:**
- [File]: [Line]: [Hardcoded secret detected]

---

### 3. PERFORMANCE

#### 3.1 Database Queries

**Check for:**
- [ ] No N+1 query problems
- [ ] Appropriate use of indexes
- [ ] Pagination for large result sets
- [ ] Avoid SELECT * (select only needed columns)

**Examples of issues:**

❌ **Bad (N+1 Query):**
```python
users = db.query(User).all()
for user in users:
    posts = db.query(Post).filter(Post.user_id == user.id).all()  # N queries!
```

✅ **Good:**
```python
users = db.query(User).options(joinedload(User.posts)).all()  # 1 query
```

**Review Notes:**
- [File]: [Line]: [N+1 query detected]

---

#### 3.2 API Calls

**Check for:**
- [ ] No unnecessary API calls in loops
- [ ] Caching where appropriate
- [ ] Batch operations instead of individual calls
- [ ] Timeouts configured

**Examples of issues:**

❌ **Bad:**
```python
for user_id in user_ids:
    user_data = external_api.get_user(user_id)  # N API calls!
```

✅ **Good:**
```python
users_data = external_api.get_users_batch(user_ids)  # 1 API call
```

**Review Notes:**
- [File]: [Line]: [Inefficient API usage]

---

#### 3.3 Frontend Performance

**Check for:**
- [ ] No unnecessary re-renders (React)
- [ ] Large lists virtualized
- [ ] Images optimized/lazy loaded
- [ ] Bundle size reasonable

**Examples of issues:**

❌ **Bad:**
```jsx
function ProductList({ products }) {
  return products.map(p => <ProductCard key={p.id} product={p} />);
  // If 10,000 products, renders 10,000 components!
}
```

✅ **Good:**
```jsx
import { VirtualList } from 'react-virtual';

function ProductList({ products }) {
  return <VirtualList items={products} renderItem={(p) => <ProductCard product={p} />} />;
  // Only renders visible items
}
```

**Review Notes:**
- [File]: [Line]: [Performance issue - [description]]

---

### 4. TESTING

#### 4.1 Test Coverage

**Check for:**
- [ ] Happy path tested
- [ ] Error cases tested
- [ ] Edge cases tested
- [ ] Critical paths have tests

**Review:**
!pytest --cov=$1 --cov-report=term-missing

**Identify untested code:**
- [File]: [Lines X-Y]: [No tests for this function]

---

#### 4.2 Test Quality

**Check for:**
- [ ] Tests are readable (clear what they're testing)
- [ ] Tests are isolated (no shared state)
- [ ] Tests use descriptive names
- [ ] No tests checking implementation details

**Examples of issues:**

❌ **Bad:**
```python
def test_1():  # What does this test?
    x = func()
    assert x == 5  # Why 5?
```

✅ **Good:**
```python
def test_calculate_discount_returns_20_percent_for_premium_users():
    user = create_premium_user()
    discount = calculate_discount(user)
    assert discount == 0.20
```

**Review Notes:**
- [Test file]: [Test name]: [Test quality issue]

---

### 5. ARCHITECTURE

#### 5.1 Separation of Concerns

**Check for:**
- [ ] Business logic in service layer (not in controllers/views)
- [ ] Data access in repository/DAO layer
- [ ] UI logic in presentation layer
- [ ] No circular dependencies

**Examples of violations:**

❌ **Bad:**
```python
@app.post("/users")
def create_user(user: UserCreate):
    # Business logic in controller!
    if not user.email.endswith("@company.com"):
        raise ValueError("Only company emails allowed")
    hashed_password = bcrypt.hash(user.password)
    db.save(User(email=user.email, password=hashed_password))
```

✅ **Good:**
```python
@app.post("/users")
def create_user(user: UserCreate):
    # Delegate to service layer
    return user_service.create_user(user)

# In user_service.py
def create_user(user: UserCreate) -> User:
    validate_company_email(user.email)
    hashed_password = hash_password(user.password)
    return user_repository.save(user)
```

**Review Notes:**
- [File]: [Line]: [Violation of separation of concerns]

---

#### 5.2 Dependencies

**Check for:**
- [ ] No unnecessary dependencies
- [ ] Dependency versions pinned
- [ ] Security vulnerabilities in dependencies

**Review:**
!pip list --outdated  # Python
!npm audit  # JavaScript

**Review Notes:**
- [Dependency]: [Version]: [Issue - e.g., "known security vulnerability"]

---

## REVIEW REPORT

**Code Reviewed:** $1
**Focus:** $2
**Reviewer:** [Your name / AI]
**Date:** [DATE]

---

### Summary

**Overall Assessment:** [✅ APPROVED / ⚠️ APPROVED WITH COMMENTS / ❌ CHANGES REQUIRED]

**Issues Found:**
- **Critical (P0):** [X] (must fix before merge)
- **Important (P1):** [X] (should fix before merge)
- **Minor (P2):** [X] (nice to fix, not blocking)
- **Nit (P3):** [X] (style suggestions, optional)

---

### Critical Issues (P0)

**Issue 1:**
- **File:** [path/to/file.py]
- **Line:** [123]
- **Category:** [Security / Performance / Bug]
- **Description:** [What's wrong]
- **Recommendation:** [How to fix]
- **Example:**
  ```python
  # Bad
  [current code]

  # Good
  [suggested fix]
  ```

**Issue 2:**
[Same structure]

---

### Important Issues (P1)

**Issue 1:**
[Same structure as P0]

---

### Minor Issues (P2)

**Issue 1:**
[Same structure]

---

### Positive Observations

**What's good about this code:**
- [Positive 1 - e.g., "Excellent test coverage (95%)"]
- [Positive 2 - e.g., "Clear naming conventions"]
- [Positive 3 - e.g., "Good error handling"]

---

### Suggestions for Improvement

**Non-blocking suggestions:**
1. [Suggestion 1 - e.g., "Consider extracting this logic to a helper function"]
2. [Suggestion 2]

---

### Follow-Up Actions

**For Code Author:**
- [ ] Fix all P0 issues
- [ ] Fix P1 issues (or discuss if not applicable)
- [ ] Consider P2/P3 suggestions
- [ ] Re-request review after fixes

**For Reviewer (after fixes):**
- [ ] Re-review fixed issues
- [ ] Approve if all P0/P1 resolved

---

## DECISION

**Status:** [✅ APPROVED / ⚠️ APPROVED WITH MINOR CHANGES / ❌ CHANGES REQUIRED]

**Rationale:**
[Explain decision - why approved or why changes required]

**Next Steps:**
[What should happen next]

---

```

---

## REVIEW BEST PRACTICES

### 1. Review in Multiple Passes

**Pass 1: High-level (5 min)**
- Architecture and design
- Overall approach makes sense?
- Separation of concerns

**Pass 2: Line-by-line (15-30 min)**
- Code quality
- Security issues
- Performance issues

**Pass 3: Testing (10 min)**
- Test coverage
- Test quality

**Pass 4: Final check (5 min)**
- Summary of findings
- Prioritize issues

**Total time:** ~30-50 minutes per feature

---

### 2. Be Specific and Constructive

❌ **Bad feedback:**
"This code is bad"

✅ **Good feedback:**
"This function violates SRP - it's doing validation, business logic, and data access. Consider splitting into validate_user(), create_user_record(), and save_user()."

---

### 3. Provide Examples

Always show:
- What's wrong (current code)
- How to fix (suggested code)

**Example:**
```
**Issue:** Magic number (line 45)

❌ Bad:
if user.age < 18:

✅ Good:
MINIMUM_AGE = 18
if user.age < MINIMUM_AGE:
```

---

### 4. Prioritize Issues

Not all issues are equal:
- **P0 (Critical):** Security vulnerabilities, data corruption bugs
- **P1 (Important):** Performance issues, missing tests for critical paths
- **P2 (Minor):** Code quality, minor performance improvements
- **P3 (Nit):** Style preferences, suggestions

**Don't block merge on P3 issues.**

---

### 5. Acknowledge Good Code

Don't just focus on negatives:
- Call out clever solutions
- Recognize good tests
- Appreciate clear documentation

**Positive reinforcement encourages good practices.**

---

## AI-ASSISTED CODE REVIEW

### Prompt for AI Code Review

```
Perform a comprehensive code review on [FILE/FEATURE].

Use the checklist from ai-project-playbook/templates/code-review.md

Review categories:
1. Code Quality (readability, SRP, DRY, error handling)
2. Security (input validation, auth, secrets)
3. Performance (DB queries, API calls, frontend)
4. Testing (coverage, quality)
5. Architecture (separation of concerns, dependencies)

For each issue found:
- Specify file and line number
- Categorize (P0/P1/P2/P3)
- Provide specific recommendation with code example

Output a review report following the template.
```

---

## INTEGRATION WITH PIV LOOP

**When to Code Review:**

**Option 1: After Implementation, Before Merge**
```
Plan → Implement → Validate → Code Review → Merge
```

**Option 2: As Part of Validation (Level 5)**
```
Plan → Implement → Validate (includes Code Review as Level 5) → Merge
```

**Recommended:** Option 2 (code review is part of validation)

---

## EXAMPLES

### Example 1: Quick Security Review

```bash
/code-review app/api/auth.py security
```

**Output:**
```
🔒 Security Review: app/api/auth.py

✅ No SQL injection (using parameterized queries)
✅ Passwords hashed (bcrypt)
❌ P0: JWT secret hardcoded (line 12)
   Recommendation: Load from environment variable
⚠️ P1: No rate limiting on login endpoint (line 45)
   Recommendation: Add rate limiter to prevent brute force

Status: ❌ CHANGES REQUIRED
Fix P0 before merging.
```

---

### Example 2: Full Code Review

```bash
/code-review feature/user-roles full
```

**Output:**
```
📋 Full Code Review: User Roles Feature

**Summary:**
- Files reviewed: 8
- Lines of code: 450
- Issues found: 12 (2 P0, 4 P1, 5 P2, 1 P3)

**Critical Issues:**
P0-1: Missing authorization check (app/api/roles.py:23)
P0-2: SQL injection vulnerability (app/services/roles.py:56)

**Important Issues:**
P1-1: N+1 query detected (app/services/users.py:34)
P1-2: No tests for edge case (tests/test_roles.py:missing)
... [full report]

Status: ❌ CHANGES REQUIRED
```

---

## CUSTOMIZATION FOR YOUR PROJECT

Add project-specific checks:

```markdown
### 6. PROJECT-SPECIFIC CHECKS

#### 6.1 Event Sourcing Patterns

**Check for:**
- [ ] Events are immutable
- [ ] Event names follow convention (PastTense)
- [ ] Projections handle all event types

#### 6.2 Multi-Tenancy

**Check for:**
- [ ] All queries filter by tenant_id
- [ ] No cross-tenant data leakage
- [ ] Tenant context set in middleware
```

---

## REFERENCES

**Related Files:**
- `validate-command.md` - Validation pyramid (code review is Level 5)
- `CLAUDE.md` - Project standards (what to review against)
- `plan-template.md` - Plans define what should be reviewed

**External:**
- OWASP Top 10: https://owasp.org/Top10/
- Code Review Best Practices: https://google.github.io/eng-practices/review/

---

**🎯 Remember: Code review is not about finding faults, it's about ensuring quality.**

**Good reviews make good code better. 🚀**
