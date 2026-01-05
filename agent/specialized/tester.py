"""
Tester Agent

Specialized agent for writing and running tests.
Generates test code and validates implementations.
"""

from agent.factory.base import BaseAgent, AgentContext, AgentResult, AgentRole


class TesterAgent(BaseAgent):
    """
    Agent specialized in testing.

    Capabilities:
    - Generate test cases
    - Write unit tests
    - Create integration tests
    - Run validation commands
    """

    def __init__(self, name: str = "tester"):
        super().__init__(
            name=name,
            role=AgentRole.TESTER,
            description="Writes tests and validates code implementations",
            tools=[],
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute testing task.

        Args:
            context: Context with code to test

        Returns:
            AgentResult with test code and validation results
        """
        task = context.task
        shared_state = context.shared_state

        try:
            # Get code from previous agents
            code_to_test = shared_state.get("generated_code", "")
            code_type = shared_state.get("code_type", "generic")

            # Generate tests
            test_code = self._generate_tests(code_to_test, code_type)
            validation_commands = self._get_validation_commands(code_type)

            output = f"""## Tests for: {task}

### Generated Test Code

```python
{test_code}
```

### Validation Commands

Run these commands to validate the implementation:

```bash
{validation_commands}
```

### Test Coverage Targets
- Unit tests: 80%+ coverage
- Integration tests: Critical paths
- Edge cases: Documented

### Next Steps
1. Save the test file
2. Run the tests
3. Fix any failures
4. Check coverage report
"""

            return AgentResult(
                success=True,
                output=output,
                data={
                    "test_code": test_code,
                    "validation_commands": validation_commands,
                    "code_type": code_type,
                },
                metadata={"agent_name": self.name},
            )

        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Test generation failed: {str(e)}",
                errors=[str(e)],
                metadata={"agent_name": self.name},
            )

    def _generate_tests(self, code: str, code_type: str) -> str:
        """Generate test code based on the implementation."""
        templates = {
            "api_endpoint": '''import pytest
from httpx import AsyncClient
from fastapi import status


class TestResourceEndpoints:
    """Tests for resource API endpoints."""

    @pytest.fixture
    async def client(self, app):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.mark.asyncio
    async def test_create_resource_returns_201(self, client):
        """Test creating a resource returns 201 Created."""
        # Arrange
        data = {"name": "Test Resource", "description": "Test"}

        # Act
        response = await client.post("/api/v1/resources", json=data)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == "Test Resource"

    @pytest.mark.asyncio
    async def test_get_resource_returns_404_when_not_found(self, client):
        """Test getting non-existent resource returns 404."""
        response = await client.get("/api/v1/resources/nonexistent-id")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_resource_returns_422_with_invalid_data(self, client):
        """Test creating resource with invalid data returns 422."""
        data = {}  # Missing required fields

        response = await client.post("/api/v1/resources", json=data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
''',
            "service": '''import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4


class TestResourceService:
    """Tests for ResourceService."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        repo = AsyncMock()
        repo.get_by_id = AsyncMock()
        repo.create = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mock repository."""
        from src.services.resource import ResourceService
        return ResourceService(mock_repository)

    @pytest.mark.asyncio
    async def test_get_resource_returns_resource_when_exists(
        self, service, mock_repository
    ):
        """Test getting existing resource."""
        # Arrange
        resource_id = uuid4()
        expected = {"id": str(resource_id), "name": "Test"}
        mock_repository.get_by_id.return_value = expected

        # Act
        result = await service.get_resource(resource_id)

        # Assert
        assert result == expected
        mock_repository.get_by_id.assert_awaited_once_with(resource_id)

    @pytest.mark.asyncio
    async def test_get_resource_returns_none_when_not_found(
        self, service, mock_repository
    ):
        """Test getting non-existent resource."""
        mock_repository.get_by_id.return_value = None

        result = await service.get_resource(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_create_resource_calls_repository_create(
        self, service, mock_repository
    ):
        """Test creating resource calls repository."""
        data = {"name": "New Resource"}
        mock_repository.create.return_value = {"id": "123", **data}

        result = await service.create_resource(data)

        assert result["name"] == "New Resource"
        mock_repository.create.assert_awaited_once()
''',
            "data_model": '''import pytest
from datetime import datetime
from uuid import UUID


class TestResourceModel:
    """Tests for Resource model."""

    def test_model_creates_with_defaults(self):
        """Test model creates with default values."""
        from src.models.resource import Resource

        resource = Resource(name="Test")

        assert resource.name == "Test"
        assert isinstance(resource.id, UUID)
        assert isinstance(resource.created_at, datetime)

    def test_model_validates_required_fields(self):
        """Test model requires name field."""
        from src.models.resource import Resource
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Resource()  # Missing name

    def test_model_serializes_to_dict(self):
        """Test model serializes correctly."""
        from src.models.resource import Resource

        resource = Resource(name="Test", description="A test")
        data = resource.model_dump()

        assert data["name"] == "Test"
        assert data["description"] == "A test"
        assert "id" in data
''',
            "component": '''import { render, screen, fireEvent } from "@testing-library/react";
import { ResourceCard } from "./ResourceCard";

describe("ResourceCard", () => {
  const defaultProps = {
    id: "123",
    name: "Test Resource",
    description: "Test description",
  };

  it("renders resource name", () => {
    render(<ResourceCard {...defaultProps} />);

    expect(screen.getByText("Test Resource")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<ResourceCard {...defaultProps} />);

    expect(screen.getByText("Test description")).toBeInTheDocument();
  });

  it("calls onEdit when edit button clicked", () => {
    const onEdit = jest.fn();
    render(<ResourceCard {...defaultProps} onEdit={onEdit} />);

    fireEvent.click(screen.getByText("Edit"));

    expect(onEdit).toHaveBeenCalledWith("123");
  });

  it("calls onDelete when delete button clicked", () => {
    const onDelete = jest.fn();
    render(<ResourceCard {...defaultProps} onDelete={onDelete} />);

    fireEvent.click(screen.getByText("Delete"));

    expect(onDelete).toHaveBeenCalledWith("123");
  });
});
''',
        }

        return templates.get(code_type, self._generic_test_template())

    def _generic_test_template(self) -> str:
        """Generate generic test template."""
        return '''import pytest


class TestFeature:
    """Tests for the feature implementation."""

    @pytest.fixture
    def setup(self):
        """Set up test fixtures."""
        # Add setup code here
        yield
        # Add teardown code here

    def test_should_perform_expected_behavior(self, setup):
        """Test the main functionality."""
        # Arrange
        expected = "expected result"

        # Act
        result = "expected result"  # Replace with actual call

        # Assert
        assert result == expected

    def test_should_handle_edge_case(self, setup):
        """Test edge case handling."""
        # Test edge cases here
        pass

    def test_should_raise_error_on_invalid_input(self, setup):
        """Test error handling."""
        with pytest.raises(ValueError):
            # Call with invalid input
            pass
'''

    def _get_validation_commands(self, code_type: str) -> str:
        """Get validation commands based on code type."""
        if code_type == "component":
            return """# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Type check
npx tsc --noEmit

# Lint
npm run lint"""
        else:
            return """# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Type check
mypy src/

# Lint
ruff check src/

# Format check
ruff format --check src/"""

    def can_handle(self, task: str) -> bool:
        """Check if this agent can handle the task."""
        testing_keywords = [
            "test", "testing", "verify", "validate",
            "coverage", "qa", "quality", "check",
        ]
        task_lower = task.lower()
        return any(kw in task_lower for kw in testing_keywords)
