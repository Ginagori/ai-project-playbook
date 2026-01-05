"""
Planner Agent

Specialized agent for creating implementation plans.
Breaks down tasks into actionable steps.
"""

from agent.factory.base import BaseAgent, AgentContext, AgentResult, AgentRole


class PlannerAgent(BaseAgent):
    """
    Agent specialized in creating implementation plans.

    Capabilities:
    - Break down features into tasks
    - Create step-by-step plans
    - Identify dependencies
    - Estimate complexity
    """

    def __init__(self, name: str = "planner"):
        super().__init__(
            name=name,
            role=AgentRole.PLANNER,
            description="Creates detailed implementation plans for features",
            tools=[],
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute planning task.

        Args:
            context: Context with the feature to plan

        Returns:
            AgentResult with implementation plan
        """
        task = context.task
        shared_state = context.shared_state

        try:
            # Get any research from previous agents
            research_data = shared_state.get("research", {})

            # Generate plan
            plan = self._generate_plan(task, research_data)

            output = f"""## Implementation Plan: {task}

{plan}

### PIV Loop Reminder
1. **Plan** (current step) - Break down the task
2. **Implement** - Write code following the plan
3. **Validate** - Run tests and linting

### Ready for Implementation
Reply with "start" to begin coding, or "modify" to adjust the plan.
"""

            return AgentResult(
                success=True,
                output=output,
                data={
                    "plan": plan,
                    "task": task,
                    "next_task": task,  # Pass to coder
                },
                metadata={"agent_name": self.name},
            )

        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Planning failed: {str(e)}",
                errors=[str(e)],
                metadata={"agent_name": self.name},
            )

    def _generate_plan(self, task: str, research_data: dict) -> str:
        """Generate implementation plan."""
        task_lower = task.lower()

        # Detect task type and generate appropriate plan
        if any(kw in task_lower for kw in ["api", "endpoint"]):
            return self._api_plan(task)
        elif any(kw in task_lower for kw in ["auth", "login", "authentication"]):
            return self._auth_plan(task)
        elif any(kw in task_lower for kw in ["database", "model", "schema"]):
            return self._database_plan(task)
        elif any(kw in task_lower for kw in ["component", "ui", "frontend"]):
            return self._frontend_plan(task)
        elif any(kw in task_lower for kw in ["test", "testing"]):
            return self._testing_plan(task)
        else:
            return self._generic_plan(task)

    def _api_plan(self, task: str) -> str:
        return """### Phase 1: Setup
- [ ] Create router file in `src/api/v1/`
- [ ] Define Pydantic schemas for request/response
- [ ] Set up dependency injection

### Phase 2: Implementation
- [ ] Implement CRUD endpoints
- [ ] Add input validation
- [ ] Implement error handling
- [ ] Add pagination for list endpoints

### Phase 3: Testing
- [ ] Write unit tests for each endpoint
- [ ] Add integration tests
- [ ] Test error cases

### Phase 4: Documentation
- [ ] Add OpenAPI docstrings
- [ ] Update API documentation

### Files to Create/Modify
```
src/api/v1/
├── router.py        # API endpoints
├── schemas.py       # Pydantic models
├── dependencies.py  # Dependency injection
tests/api/v1/
├── test_router.py   # Endpoint tests
```

### Validation Commands
```bash
pytest tests/api/v1/ -v
mypy src/api/v1/
ruff check src/api/v1/
```
"""

    def _auth_plan(self, task: str) -> str:
        return """### Phase 1: User Model
- [ ] Create User model with email, password_hash
- [ ] Add database migration
- [ ] Implement password hashing (bcrypt)

### Phase 2: Auth Endpoints
- [ ] POST /auth/signup - Create user
- [ ] POST /auth/login - Authenticate and return JWT
- [ ] POST /auth/refresh - Refresh access token
- [ ] POST /auth/logout - Invalidate token

### Phase 3: Middleware
- [ ] Create JWT validation middleware
- [ ] Add current_user dependency
- [ ] Implement role-based access control

### Phase 4: Security
- [ ] Add rate limiting
- [ ] Implement password requirements
- [ ] Add account lockout after failed attempts

### Files to Create/Modify
```
src/auth/
├── models.py        # User model
├── router.py        # Auth endpoints
├── service.py       # Auth logic
├── schemas.py       # Auth schemas
├── middleware.py    # JWT middleware
├── utils.py         # Password hashing
```

### Validation Commands
```bash
pytest tests/auth/ -v
# Manual test: signup -> login -> access protected route
```
"""

    def _database_plan(self, task: str) -> str:
        return """### Phase 1: Schema Design
- [ ] Identify all entities from PRD
- [ ] Define relationships (1:1, 1:N, N:M)
- [ ] Plan indexes for common queries

### Phase 2: Models
- [ ] Create base model with id, timestamps
- [ ] Implement entity models
- [ ] Add foreign key relationships
- [ ] Create Pydantic schemas

### Phase 3: Migrations
- [ ] Generate migration files
- [ ] Add seed data for development
- [ ] Test rollback capability

### Phase 4: Repository Layer
- [ ] Create repository interface
- [ ] Implement CRUD operations
- [ ] Add query methods

### Files to Create/Modify
```
src/models/
├── base.py          # Base model
├── user.py          # User model
├── [entity].py      # Other entities
migrations/
├── 001_initial.sql  # Initial schema
├── 002_seed.sql     # Seed data
```

### Validation Commands
```bash
# Apply migrations
supabase db push
# Verify schema
supabase db diff
```
"""

    def _frontend_plan(self, task: str) -> str:
        return """### Phase 1: Component Structure
- [ ] Create component file
- [ ] Define TypeScript interfaces
- [ ] Set up component props

### Phase 2: Implementation
- [ ] Build basic layout
- [ ] Add styling (Tailwind)
- [ ] Implement interactivity
- [ ] Add loading states

### Phase 3: Data Fetching
- [ ] Create custom hook for data
- [ ] Implement error handling
- [ ] Add optimistic updates

### Phase 4: Testing
- [ ] Write component tests
- [ ] Add accessibility tests
- [ ] Test responsive design

### Files to Create/Modify
```
src/components/
├── [Component]/
│   ├── index.tsx        # Main component
│   ├── [Component].test.tsx
│   └── types.ts         # TypeScript types
src/hooks/
├── use[Data].ts         # Data hook
```

### Validation Commands
```bash
npm run lint
npm run test
npm run build
```
"""

    def _testing_plan(self, task: str) -> str:
        return """### Phase 1: Test Structure
- [ ] Create test file mirroring source
- [ ] Set up fixtures
- [ ] Create mock dependencies

### Phase 2: Unit Tests
- [ ] Test happy path
- [ ] Test edge cases
- [ ] Test error handling

### Phase 3: Integration Tests
- [ ] Test API endpoints
- [ ] Test database operations
- [ ] Test external service calls

### Phase 4: Coverage
- [ ] Run coverage report
- [ ] Add tests for uncovered code
- [ ] Target 80%+ coverage

### Test Pattern
```python
class TestFeature:
    @pytest.fixture
    def setup(self):
        # Setup code
        pass

    def test_should_do_something_when_condition(self, setup):
        # Arrange
        # Act
        # Assert
        pass
```

### Validation Commands
```bash
pytest tests/ -v --cov=src --cov-report=html
```
"""

    def _generic_plan(self, task: str) -> str:
        return f"""### Phase 1: Research
- [ ] Understand requirements from PRD
- [ ] Review existing code patterns
- [ ] Identify dependencies

### Phase 2: Design
- [ ] Define data structures
- [ ] Plan file organization
- [ ] Identify interfaces

### Phase 3: Implementation
- [ ] Create necessary files
- [ ] Implement core logic
- [ ] Add error handling
- [ ] Write documentation

### Phase 4: Testing
- [ ] Write unit tests
- [ ] Test edge cases
- [ ] Verify integration

### Task Breakdown for: {task}
1. Research existing patterns
2. Create file structure
3. Implement core functionality
4. Add validation and error handling
5. Write tests
6. Document the code

### Validation Commands
```bash
pytest tests/ -v
mypy src/
ruff check src/
```
"""

    def can_handle(self, task: str) -> bool:
        """Check if this agent can handle the task."""
        planning_keywords = [
            "plan", "design", "architect", "structure",
            "organize", "break down", "outline", "spec",
        ]
        task_lower = task.lower()
        return any(kw in task_lower for kw in planning_keywords)
