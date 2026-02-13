"""
Artifact Evaluator

Evaluates generated artifacts (CLAUDE.md, PRD, feature plans) using rule-based checks.
Returns quality scores and suggestions for improvement.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agent.evals.rules import (
    CheckResult,
    has_required_sections,
    no_placeholder_text,
    has_tech_stack_specifics,
    has_validation_commands,
    has_file_references,
    minimum_length,
    has_success_criteria,
    has_feature_prioritization,
    has_code_examples,
    has_architecture_pattern,
    has_integration_points,
)


@dataclass
class EvalResult:
    """Result of evaluating an artifact."""
    artifact_type: str
    passed: bool
    score: float  # 0.0 to 1.0
    checks: list[CheckResult] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "artifact_type": self.artifact_type,
            "passed": self.passed,
            "score": round(self.score, 3),
            "checks_passed": sum(1 for c in self.checks if c.passed),
            "checks_total": len(self.checks),
            "critical_failures": [
                c.message for c in self.checks
                if not c.passed and c.severity == "critical"
            ],
            "suggestions": self.suggestions,
        }

    def format_report(self) -> str:
        """Format as a readable report."""
        status = "PASSED" if self.passed else "NEEDS IMPROVEMENT"
        lines = [
            f"### Artifact Evaluation: {self.artifact_type}",
            f"**Status**: {status} | **Score**: {self.score:.0%}",
            "",
        ]

        # Group by severity
        critical = [c for c in self.checks if c.severity == "critical"]
        warnings = [c for c in self.checks if c.severity == "warning"]
        info = [c for c in self.checks if c.severity == "info"]

        if critical:
            lines.append("**Critical Checks:**")
            for c in critical:
                icon = "PASS" if c.passed else "FAIL"
                lines.append(f"- [{icon}] {c.message}")

        if warnings:
            lines.append("\n**Quality Checks:**")
            for c in warnings:
                icon = "PASS" if c.passed else "WARN"
                lines.append(f"- [{icon}] {c.message}")

        if info:
            lines.append("\n**Info:**")
            for c in info:
                icon = "PASS" if c.passed else "INFO"
                lines.append(f"- [{icon}] {c.message}")

        if self.suggestions:
            lines.append("\n**Suggestions:**")
            for s in self.suggestions:
                lines.append(f"- {s}")

        return "\n".join(lines)


class ArtifactEvaluator:
    """Evaluates generated artifacts using configurable rule-based checks."""

    def evaluate_claude_md(self, content: str) -> EvalResult:
        """
        Evaluate a CLAUDE.md file.

        Checks:
        - Required sections (Core Principles, Tech Stack, Architecture, etc.)
        - No placeholder text
        - Specific tech stack mentions
        - Code examples present
        - Architecture pattern specified
        - Minimum length
        """
        checks = [
            has_required_sections(content, "claude_md"),
            no_placeholder_text(content),
            has_tech_stack_specifics(content),
            has_code_examples(content),
            has_architecture_pattern(content),
            minimum_length(content, artifact_type="claude_md"),
        ]

        return self._build_result("claude_md", checks)

    def evaluate_prd(self, content: str) -> EvalResult:
        """
        Evaluate a PRD (Product Requirements Document).

        Checks:
        - Required sections (Executive Summary, MVP Scope, etc.)
        - No placeholder text
        - Success criteria defined
        - Feature prioritization present
        - Tech stack mentioned
        - Minimum length
        """
        checks = [
            has_required_sections(content, "prd"),
            no_placeholder_text(content),
            has_success_criteria(content),
            has_feature_prioritization(content),
            has_tech_stack_specifics(content),
            minimum_length(content, artifact_type="prd"),
        ]

        return self._build_result("prd", checks)

    def evaluate_plan(self, content: str) -> EvalResult:
        """
        Evaluate a feature implementation plan.

        Checks:
        - Required sections (Files, Tasks)
        - File references present
        - Validation commands included
        - Integration points mentioned
        - No placeholder text
        - Minimum length
        """
        checks = [
            has_required_sections(content, "plan"),
            has_file_references(content),
            has_validation_commands(content),
            has_integration_points(content),
            no_placeholder_text(content),
            minimum_length(content, artifact_type="plan"),
        ]

        return self._build_result("plan", checks)

    def evaluate(self, artifact_type: str, content: str) -> EvalResult:
        """
        Evaluate any artifact by type.

        Args:
            artifact_type: One of "claude_md", "prd", "plan"
            content: The artifact content to evaluate

        Returns:
            EvalResult with scores and suggestions
        """
        evaluators = {
            "claude_md": self.evaluate_claude_md,
            "prd": self.evaluate_prd,
            "plan": self.evaluate_plan,
        }

        evaluator = evaluators.get(artifact_type)
        if not evaluator:
            return EvalResult(
                artifact_type=artifact_type,
                passed=False,
                score=0.0,
                suggestions=[f"Unknown artifact type: {artifact_type}. Use: claude_md, prd, plan"],
            )

        return evaluator(content)

    def _build_result(self, artifact_type: str, checks: list[CheckResult]) -> EvalResult:
        """Build an EvalResult from a list of checks."""
        # Calculate overall score (weighted by severity)
        severity_weights = {"critical": 3.0, "warning": 1.5, "info": 0.5}
        total_weight = 0.0
        weighted_score = 0.0

        for check in checks:
            weight = severity_weights.get(check.severity, 1.0)
            total_weight += weight
            weighted_score += check.score * weight

        overall_score = weighted_score / total_weight if total_weight > 0 else 0.0

        # Passed = no critical failures
        critical_failures = [c for c in checks if not c.passed and c.severity == "critical"]
        passed = len(critical_failures) == 0

        # Generate suggestions for failed checks
        suggestions = []
        for check in checks:
            if not check.passed:
                suggestions.append(check.message)

        return EvalResult(
            artifact_type=artifact_type,
            passed=passed,
            score=overall_score,
            checks=checks,
            suggestions=suggestions,
        )
