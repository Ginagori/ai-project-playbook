"""Project state and configuration models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProjectType(str, Enum):
    """Type of project being built."""
    SAAS = "saas"
    API = "api"
    AGENT = "agent"
    MULTI_AGENT = "multi-agent"


class ScalePhase(str, Enum):
    """Scale phase of the project."""
    MVP = "mvp"
    GROWTH = "growth"
    SCALE = "scale"
    ENTERPRISE = "enterprise"


class AutonomyMode(str, Enum):
    """Agent autonomy mode."""
    SUPERVISED = "supervised"  # Ask before actions
    AUTONOMOUS = "autonomous"  # Execute without asking
    PLAN_ONLY = "plan_only"    # Only generate plans


class Phase(str, Enum):
    """Current phase of the project."""
    DISCOVERY = "discovery"
    PLANNING = "planning"
    ROADMAP = "roadmap"
    IMPLEMENTATION = "implementation"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"


class Feature(BaseModel):
    """A feature to be implemented."""
    name: str
    description: str
    status: str = "pending"  # pending, in_progress, completed
    plan: str | None = None
    files: list[str] = Field(default_factory=list)
    tests: list[str] = Field(default_factory=list)


class TechStack(BaseModel):
    """Technology stack for the project."""
    frontend: str | None = None
    backend: str | None = None
    database: str | None = None
    auth: str | None = None
    deployment: str | None = None
    extras: dict[str, str] = Field(default_factory=dict)


class ProjectConfig(BaseModel):
    """Configuration for a project."""
    objective: str
    project_type: ProjectType | None = None
    scale: ScalePhase = ScalePhase.MVP
    mode: AutonomyMode = AutonomyMode.SUPERVISED
    tech_stack: TechStack = Field(default_factory=TechStack)
    working_dir: str | None = None


class ProjectState(BaseModel):
    """
    Complete state of a project through all phases.

    This is the main state object that flows through the LangGraph orchestrator.
    """
    # Core info
    id: str
    objective: str
    mode: AutonomyMode = AutonomyMode.SUPERVISED
    current_phase: Phase = Phase.DISCOVERY

    # Project configuration
    project_type: ProjectType | None = None
    scale: ScalePhase = ScalePhase.MVP
    tech_stack: TechStack = Field(default_factory=TechStack)

    # Generated artifacts
    claude_md: str | None = None
    prd: str | None = None

    # Features and progress
    features: list[Feature] = Field(default_factory=list)
    current_feature_index: int = 0

    # Files and validation
    files_created: list[str] = Field(default_factory=list)
    validation_results: dict[str, Any] = Field(default_factory=dict)

    # Deployment configs
    deployment_configs: dict[str, str] = Field(default_factory=dict)

    # User interaction
    needs_user_input: bool = False
    pending_question: str | None = None
    user_answers: dict[str, str] = Field(default_factory=dict)

    # Metadata
    team: str | None = None
    owner: str | None = None
    visibility: str = "private"  # private, shared

    @property
    def current_feature(self) -> Feature | None:
        """Get the current feature being implemented."""
        if 0 <= self.current_feature_index < len(self.features):
            return self.features[self.current_feature_index]
        return None

    @property
    def is_complete(self) -> bool:
        """Check if all features are completed."""
        return all(f.status == "completed" for f in self.features)

    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage."""
        if not self.features:
            return 0.0
        completed = sum(1 for f in self.features if f.status == "completed")
        return (completed / len(self.features)) * 100
