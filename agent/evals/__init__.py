"""
Artifact Evaluation Module

Provides quality checks for generated artifacts (CLAUDE.md, PRD, feature plans).
"""

from agent.evals.artifact_evaluator import ArtifactEvaluator, EvalResult
from agent.evals.rules import (
    has_required_sections,
    no_placeholder_text,
    has_tech_stack_specifics,
    has_validation_commands,
    has_file_references,
    minimum_length,
    has_success_criteria,
    has_feature_prioritization,
)

__all__ = [
    "ArtifactEvaluator",
    "EvalResult",
    "has_required_sections",
    "no_placeholder_text",
    "has_tech_stack_specifics",
    "has_validation_commands",
    "has_file_references",
    "minimum_length",
    "has_success_criteria",
    "has_feature_prioritization",
]
