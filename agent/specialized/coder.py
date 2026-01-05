"""
Coder Agent

Specialized agent for writing and modifying code.
Generates code following CLAUDE.md patterns and best practices.
"""

from agent.factory.base import BaseAgent, AgentContext, AgentResult, AgentRole


class CoderAgent(BaseAgent):
    """
    Agent specialized in writing and modifying code.

    Capabilities:
    - Generate code from specifications
    - Implement features following patterns
    - Fix bugs
    - Refactor code
    """

    def __init__(self, name: str = "coder"):
        super().__init__(
            name=name,
            role=AgentRole.CODER,
            description="Writes and modifies code following project patterns",
            tools=[],
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute coding task.

        Args:
            context: Context with the coding task

        Returns:
            AgentResult with generated code or modifications
        """
        task = context.task
        shared_state = context.shared_state

        try:
            # Get any research from previous agents
            research_data = shared_state.get("research", {})
            plan_data = shared_state.get("plan", {})

            # Generate code based on task type
            code_type = self._determine_code_type(task)
            generated_code = self._generate_code_template(code_type, task, plan_data)

            output = f"""## Code Generation for: {task}

### Generated Code

```python
{generated_code}
```

### Implementation Notes
- Follow CLAUDE.md patterns
- Add type hints to all functions
- Write tests alongside code
- Use descriptive variable names

### Next Steps
1. Review the generated code
2. Customize for your specific needs
3. Add error handling
4. Write tests
"""

            return AgentResult(
                success=True,
                output=output,
                data={
                    "code_type": code_type,
                    "generated_code": generated_code,
                    "task": task,
                },
                metadata={"agent_name": self.name},
            )

        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Code generation failed: {str(e)}",
                errors=[str(e)],
                metadata={"agent_name": self.name},
            )

    def _determine_code_type(self, task: str) -> str:
        """Determine what type of code to generate."""
        task_lower = task.lower()

        if any(kw in task_lower for kw in ["api", "endpoint", "route"]):
            return "api_endpoint"
        elif any(kw in task_lower for kw in ["model", "schema", "database"]):
            return "data_model"
        elif any(kw in task_lower for kw in ["service", "business logic"]):
            return "service"
        elif any(kw in task_lower for kw in ["component", "ui", "frontend"]):
            return "component"
        elif any(kw in task_lower for kw in ["test", "testing"]):
            return "test"
        else:
            return "generic"

    def _generate_code_template(self, code_type: str, task: str, plan_data: dict) -> str:
        """Generate code template based on type."""
        templates = {
            "api_endpoint": '''from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["resource"])


class ResourceCreate(BaseModel):
    """Schema for creating a resource."""
    name: str
    description: str | None = None


class ResourceResponse(BaseModel):
    """Schema for resource response."""
    id: str
    name: str
    description: str | None
    created_at: str


@router.post("/resources", response_model=ResourceResponse)
async def create_resource(data: ResourceCreate) -> ResourceResponse:
    """Create a new resource."""
    # TODO: Implement creation logic
    pass


@router.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(resource_id: str) -> ResourceResponse:
    """Get a resource by ID."""
    # TODO: Implement retrieval logic
    pass
''',
            "data_model": '''from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """Base model for all entities."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Resource(BaseEntity):
    """Resource entity model."""
    name: str
    description: str | None = None
    is_active: bool = True

    # For multi-tenancy
    tenant_id: UUID | None = None
''',
            "service": '''from typing import Protocol
from uuid import UUID


class ResourceRepository(Protocol):
    """Protocol for resource repository."""
    async def get_by_id(self, id: UUID) -> dict | None: ...
    async def create(self, data: dict) -> dict: ...
    async def update(self, id: UUID, data: dict) -> dict | None: ...
    async def delete(self, id: UUID) -> bool: ...


class ResourceService:
    """Service for managing resources."""

    def __init__(self, repository: ResourceRepository):
        self.repository = repository

    async def get_resource(self, resource_id: UUID) -> dict | None:
        """Get a resource by ID."""
        return await self.repository.get_by_id(resource_id)

    async def create_resource(self, data: dict) -> dict:
        """Create a new resource."""
        # Add business logic here
        return await self.repository.create(data)
''',
            "component": '''import React from "react";

interface ResourceCardProps {
  id: string;
  name: string;
  description?: string;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
}

export function ResourceCard({
  id,
  name,
  description,
  onEdit,
  onDelete,
}: ResourceCardProps) {
  return (
    <div className="p-4 border rounded-lg shadow-sm">
      <h3 className="text-lg font-semibold">{name}</h3>
      {description && (
        <p className="text-gray-600 mt-2">{description}</p>
      )}
      <div className="mt-4 flex gap-2">
        {onEdit && (
          <button onClick={() => onEdit(id)}>Edit</button>
        )}
        {onDelete && (
          <button onClick={() => onDelete(id)}>Delete</button>
        )}
      </div>
    </div>
  );
}
''',
            "test": '''import pytest
from unittest.mock import AsyncMock, MagicMock


class TestResourceService:
    """Tests for ResourceService."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mock repository."""
        from src.services.resource import ResourceService
        return ResourceService(mock_repository)

    @pytest.mark.asyncio
    async def test_get_resource_returns_resource_when_exists(
        self, service, mock_repository
    ):
        """Test getting an existing resource."""
        # Arrange
        expected = {"id": "123", "name": "Test"}
        mock_repository.get_by_id.return_value = expected

        # Act
        result = await service.get_resource("123")

        # Assert
        assert result == expected
        mock_repository.get_by_id.assert_called_once_with("123")

    @pytest.mark.asyncio
    async def test_get_resource_returns_none_when_not_exists(
        self, service, mock_repository
    ):
        """Test getting a non-existent resource."""
        mock_repository.get_by_id.return_value = None

        result = await service.get_resource("nonexistent")

        assert result is None
''',
            "generic": f'''# Generated code for: {task}

def main():
    """Main function."""
    # TODO: Implement functionality
    pass


if __name__ == "__main__":
    main()
''',
        }

        return templates.get(code_type, templates["generic"])

    def can_handle(self, task: str) -> bool:
        """Check if this agent can handle the task."""
        coding_keywords = [
            "implement", "write", "code", "create", "build",
            "fix", "bug", "refactor", "add", "modify",
            "generate", "develop",
        ]
        task_lower = task.lower()
        return any(kw in task_lower for kw in coding_keywords)
