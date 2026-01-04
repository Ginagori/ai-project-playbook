"""
File Operations Tool

Provides file system operations for the AI Project Playbook Agent.
Used to create project files like CLAUDE.md, PRD, plans, etc.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileResult:
    """Result of a file operation."""
    success: bool
    path: str
    message: str


def ensure_directory(path: Path) -> bool:
    """Ensure a directory exists, creating it if necessary."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def write_file(file_path: str, content: str, overwrite: bool = False) -> FileResult:
    """
    Write content to a file.

    Args:
        file_path: Path to the file (absolute or relative to cwd)
        content: Content to write
        overwrite: Whether to overwrite existing files

    Returns:
        FileResult with success status and message
    """
    try:
        path = Path(file_path)

        # Check if file exists and overwrite is False
        if path.exists() and not overwrite:
            return FileResult(
                success=False,
                path=str(path),
                message=f"File already exists: {path}. Use overwrite=True to replace.",
            )

        # Ensure parent directory exists
        if not ensure_directory(path.parent):
            return FileResult(
                success=False,
                path=str(path),
                message=f"Could not create directory: {path.parent}",
            )

        # Write the file
        path.write_text(content, encoding="utf-8")

        return FileResult(
            success=True,
            path=str(path),
            message=f"Successfully wrote {len(content)} characters to {path}",
        )

    except Exception as e:
        return FileResult(
            success=False,
            path=file_path,
            message=f"Error writing file: {str(e)}",
        )


def read_file(file_path: str) -> tuple[str | None, str]:
    """
    Read content from a file.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (content or None, message)
    """
    try:
        path = Path(file_path)

        if not path.exists():
            return None, f"File not found: {path}"

        content = path.read_text(encoding="utf-8")
        return content, f"Successfully read {len(content)} characters from {path}"

    except Exception as e:
        return None, f"Error reading file: {str(e)}"


def create_project_structure(
    base_path: str,
    project_name: str,
    tech_stack: dict,
) -> list[FileResult]:
    """
    Create the initial project structure.

    Args:
        base_path: Base directory for the project
        project_name: Name of the project
        tech_stack: Dictionary with frontend, backend, database info

    Returns:
        List of FileResult for each created file/directory
    """
    results = []
    base = Path(base_path) / project_name

    # Common directories
    directories = [
        ".claude/commands",
        "docs",
        "scripts",
    ]

    # Add backend-specific directories
    backend = tech_stack.get("backend", "fastapi")
    if backend in ["fastapi", "django"]:
        directories.extend([
            "src/api",
            "src/services",
            "src/models",
            "src/utils",
            "tests/unit",
            "tests/integration",
        ])
    elif backend == "express":
        directories.extend([
            "src/routes",
            "src/controllers",
            "src/models",
            "src/middleware",
            "src/utils",
            "tests",
        ])

    # Add frontend-specific directories
    frontend = tech_stack.get("frontend")
    if frontend and frontend != "none":
        directories.extend([
            "frontend/src/components",
            "frontend/src/pages",
            "frontend/src/hooks",
            "frontend/src/utils",
            "frontend/src/styles",
        ])

    # Create directories
    for dir_path in directories:
        full_path = base / dir_path
        if ensure_directory(full_path):
            results.append(FileResult(
                success=True,
                path=str(full_path),
                message=f"Created directory: {dir_path}",
            ))
        else:
            results.append(FileResult(
                success=False,
                path=str(full_path),
                message=f"Failed to create directory: {dir_path}",
            ))

    return results


def create_claude_md(
    project_path: str,
    objective: str,
    tech_stack: dict,
    project_type: str = "saas",
) -> FileResult:
    """
    Create the CLAUDE.md file for a project.

    Args:
        project_path: Path to the project directory
        objective: Project objective
        tech_stack: Dictionary with frontend, backend, database info
        project_type: Type of project (saas, api, agent, multi-agent)

    Returns:
        FileResult
    """
    frontend = tech_stack.get("frontend", "react-vite")
    backend = tech_stack.get("backend", "fastapi")
    database = tech_stack.get("database", "postgresql-supabase")

    content = f"""# {objective}

## Core Principles

- **TYPE_SAFETY**: All functions must have type hints (Python) or TypeScript strict mode
- **VERBOSE_NAMING**: Use descriptive names (get_user_by_email, not get_user)
- **AI_FRIENDLY_LOGGING**: JSON structured logs with fix_suggestion field
- **KISS**: Keep solutions simple, avoid over-engineering
- **YAGNI**: Don't build features until needed
- **SINGLE_RESPONSIBILITY**: Each function/class does one thing well

## Tech Stack

- **Frontend**: {frontend}
- **Backend**: {backend}
- **Database**: {database}
- **Package Manager**: uv (Python) / pnpm (Node)
- **Testing**: pytest (Python) / vitest (Node)
- **Linting**: ruff (Python) / eslint (Node)
- **Formatting**: ruff format (Python) / prettier (Node)

## Architecture

- **Pattern**: Vertical Slice Architecture
- **API Style**: REST with OpenAPI documentation
- **Auth**: JWT with refresh tokens
- **Multi-tenancy**: {"Row-Level Security" if project_type == "saas" else "N/A"}

## Project Structure

```
{objective.lower().replace(" ", "-")}/
├── .claude/
│   └── commands/           # Slash commands
├── src/
│   ├── api/                # API routes/endpoints
│   ├── services/           # Business logic
│   ├── models/             # Data models
│   └── utils/              # Utilities
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                   # Documentation
├── CLAUDE.md               # This file
└── README.md               # Project README
```

## Code Style

### Python
- Use snake_case for functions and variables
- Use PascalCase for classes
- Maximum line length: 100 characters
- Docstrings required for public functions
- Type hints required for all function parameters and returns

### TypeScript
- Use camelCase for functions and variables
- Use PascalCase for components and classes
- Use interfaces over types when possible
- Strict mode enabled

## Testing

- Unit tests mirror source structure (src/services/user.py → tests/unit/services/test_user.py)
- Integration tests in tests/integration/
- Minimum 80% coverage for core features
- Use descriptive test names: test_get_user_by_email_returns_none_when_not_found

## Logging

Use structured JSON logging:

```python
logger.info(
    "User created",
    extra={{
        "user_id": user.id,
        "email": user.email,
        "action": "user_create",
        "fix_suggestion": None  # Add when logging errors
    }}
)
```

## Common Patterns

### Service Pattern
```python
class UserService:
    def __init__(self, db: Database):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.db.users.find_one({{"email": email}})
```

### API Handler Pattern
```python
@router.get("/users/{{user_id}}")
async def get_user(user_id: str, service: UserService = Depends()) -> UserResponse:
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(user)
```

---

*Generated by AI Project Playbook Agent on {datetime.now().strftime("%Y-%m-%d")}*
"""

    file_path = Path(project_path) / "CLAUDE.md"
    return write_file(str(file_path), content, overwrite=True)


def create_prd(
    project_path: str,
    objective: str,
    tech_stack: dict,
    project_type: str = "saas",
    scale: str = "mvp",
) -> FileResult:
    """
    Create the PRD file for a project.

    Args:
        project_path: Path to the project directory
        objective: Project objective
        tech_stack: Dictionary with frontend, backend, database info
        project_type: Type of project
        scale: Target scale (mvp, growth, scale, enterprise)

    Returns:
        FileResult
    """
    content = f"""# Product Requirements Document

## Executive Summary

**Product**: {objective}
**Type**: {project_type.upper()}
**Target Scale**: {scale.upper()}
**Created**: {datetime.now().strftime("%Y-%m-%d")}

## Mission

Build a {project_type} application that {objective}.

## Problem Statement

[Describe the problem this product solves]

## Target Users

- **Primary**: [Primary user persona]
- **Secondary**: [Secondary user persona]

## MVP Scope

### Core Features (P0 - Must Have)

1. **User Authentication**
   - Email/password signup and login
   - Password reset flow
   - Session management with JWT

2. **Core Functionality**
   - [Feature 1 - describe]
   - [Feature 2 - describe]
   - [Feature 3 - describe]

3. **Basic Dashboard**
   - Overview of key metrics
   - Navigation to main features

### Nice-to-Have (P1)

1. Email notifications
2. User preferences/settings
3. Analytics dashboard
4. Export functionality

### Future (P2)

1. Advanced reporting
2. Integrations
3. Mobile app
4. API for third parties

## User Stories

### Authentication
- As a user, I can create an account with email and password
- As a user, I can log in to my account
- As a user, I can reset my password if forgotten
- As a user, I can log out securely

### Core Features
- As a user, I can [action] so that [benefit]
- As a user, I can [action] so that [benefit]
- As a user, I can [action] so that [benefit]

## Technical Requirements

### Tech Stack
- **Frontend**: {tech_stack.get("frontend", "N/A")}
- **Backend**: {tech_stack.get("backend", "N/A")}
- **Database**: {tech_stack.get("database", "N/A")}

### Non-Functional Requirements
- **Performance**: Page load < 3s, API response < 500ms
- **Availability**: 99.9% uptime
- **Security**: HTTPS, data encryption, OWASP compliance
- **Scalability**: Support {scale} user load

## Success Criteria

### MVP Launch
- [ ] Users can complete core workflow end-to-end
- [ ] System handles expected load
- [ ] All critical paths have test coverage (>80%)
- [ ] Deployment pipeline working
- [ ] Basic monitoring in place

### Post-Launch (30 days)
- [ ] User retention > 40%
- [ ] < 5 critical bugs
- [ ] Core features adopted by > 60% of users

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Setup | 1-2 days | Project structure, CI/CD, dev environment |
| Auth | 2-3 days | Signup, login, password reset |
| Core | 1-2 weeks | Main features |
| Polish | 3-5 days | Bug fixes, UX improvements |
| Launch | 1-2 days | Deployment, monitoring |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | High | Strict MVP definition, feature freeze |
| Technical debt | Medium | Code reviews, testing requirements |
| Performance issues | Medium | Load testing, monitoring |

---

*Generated by AI Project Playbook Agent on {datetime.now().strftime("%Y-%m-%d")}*
"""

    file_path = Path(project_path) / "docs" / "PRD.md"
    # Ensure docs directory exists
    ensure_directory(Path(project_path) / "docs")
    return write_file(str(file_path), content, overwrite=True)
