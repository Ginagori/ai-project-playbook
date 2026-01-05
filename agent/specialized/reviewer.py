"""
Reviewer Agent

Specialized agent for reviewing code and providing feedback.
Checks for best practices, security issues, and code quality.
"""

from agent.factory.base import BaseAgent, AgentContext, AgentResult, AgentRole


class ReviewerAgent(BaseAgent):
    """
    Agent specialized in reviewing code.

    Capabilities:
    - Check code quality
    - Identify security issues
    - Suggest improvements
    - Verify adherence to patterns
    """

    def __init__(self, name: str = "reviewer"):
        super().__init__(
            name=name,
            role=AgentRole.REVIEWER,
            description="Reviews code for quality, security, and best practices",
            tools=[],
        )
        self._review_criteria = [
            "type_safety",
            "naming_conventions",
            "error_handling",
            "security",
            "performance",
            "testing",
            "documentation",
        ]

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute code review.

        Args:
            context: Context with code to review

        Returns:
            AgentResult with review feedback
        """
        task = context.task
        shared_state = context.shared_state

        try:
            # Get code from previous agent or context
            code_to_review = shared_state.get("generated_code", "")
            code_type = shared_state.get("code_type", "unknown")

            # Perform review
            review_results = self._perform_review(code_to_review, code_type)

            # Generate output
            output = self._format_review_output(task, review_results)

            # Determine overall success
            critical_issues = [
                r for r in review_results
                if r["severity"] == "critical"
            ]

            return AgentResult(
                success=len(critical_issues) == 0,
                output=output,
                data={
                    "review_results": review_results,
                    "issues_count": len(review_results),
                    "critical_count": len(critical_issues),
                },
                metadata={"agent_name": self.name},
                next_agent="coder" if critical_issues else None,
            )

        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Review failed: {str(e)}",
                errors=[str(e)],
                metadata={"agent_name": self.name},
            )

    def _perform_review(self, code: str, code_type: str) -> list[dict]:
        """Perform code review checks."""
        issues = []

        # Type safety check
        if "def " in code and "->" not in code:
            issues.append({
                "criterion": "type_safety",
                "severity": "warning",
                "message": "Functions missing return type hints",
                "suggestion": "Add return type hints to all functions (e.g., def func() -> str:)",
            })

        if "def " in code and ": " not in code.split("def ")[1].split(")")[0]:
            issues.append({
                "criterion": "type_safety",
                "severity": "warning",
                "message": "Function parameters missing type hints",
                "suggestion": "Add type hints to all parameters (e.g., def func(name: str):)",
            })

        # Security checks
        security_issues = self._check_security(code)
        issues.extend(security_issues)

        # Error handling check
        if "try:" not in code and ("await" in code or "async" in code):
            issues.append({
                "criterion": "error_handling",
                "severity": "info",
                "message": "Async code without try/except blocks",
                "suggestion": "Consider adding error handling for async operations",
            })

        # Documentation check
        if "def " in code and '"""' not in code and "'''" not in code:
            issues.append({
                "criterion": "documentation",
                "severity": "info",
                "message": "Functions missing docstrings",
                "suggestion": "Add docstrings to document function purpose and parameters",
            })

        # TODO check
        if "TODO" in code or "FIXME" in code:
            issues.append({
                "criterion": "completeness",
                "severity": "warning",
                "message": "Code contains TODO/FIXME comments",
                "suggestion": "Complete all TODO items before merging",
            })

        # Testing check
        if code_type != "test" and "test_" not in code:
            issues.append({
                "criterion": "testing",
                "severity": "info",
                "message": "No tests found for this code",
                "suggestion": "Write unit tests for all public functions",
            })

        return issues

    def _check_security(self, code: str) -> list[dict]:
        """Check for common security issues."""
        issues = []

        # SQL injection
        if "execute(" in code and "f'" in code or 'f"' in code:
            issues.append({
                "criterion": "security",
                "severity": "critical",
                "message": "Potential SQL injection vulnerability",
                "suggestion": "Use parameterized queries instead of f-strings",
            })

        # Hardcoded secrets
        secret_patterns = ["password=", "api_key=", "secret=", "token="]
        for pattern in secret_patterns:
            if pattern in code.lower() and "=" in code:
                issues.append({
                    "criterion": "security",
                    "severity": "critical",
                    "message": f"Possible hardcoded secret: {pattern}",
                    "suggestion": "Use environment variables for secrets",
                })
                break

        # Eval usage
        if "eval(" in code or "exec(" in code:
            issues.append({
                "criterion": "security",
                "severity": "critical",
                "message": "Use of eval() or exec() detected",
                "suggestion": "Avoid eval/exec - use safer alternatives",
            })

        return issues

    def _format_review_output(self, task: str, results: list[dict]) -> str:
        """Format review results for output."""
        if not results:
            return f"""## Code Review: {task}

### Result: PASSED

No issues found. Code looks good!

### Checklist
- [x] Type safety
- [x] Naming conventions
- [x] Error handling
- [x] Security
- [x] Documentation
"""

        # Group by severity
        critical = [r for r in results if r["severity"] == "critical"]
        warnings = [r for r in results if r["severity"] == "warning"]
        info = [r for r in results if r["severity"] == "info"]

        output = f"""## Code Review: {task}

### Result: {"FAILED - Critical Issues" if critical else "PASSED with warnings" if warnings else "PASSED"}

### Summary
- Critical: {len(critical)}
- Warnings: {len(warnings)}
- Info: {len(info)}

"""

        if critical:
            output += "### Critical Issues (Must Fix)\n\n"
            for issue in critical:
                output += f"- **{issue['criterion']}**: {issue['message']}\n"
                output += f"  - Suggestion: {issue['suggestion']}\n\n"

        if warnings:
            output += "### Warnings (Should Fix)\n\n"
            for issue in warnings:
                output += f"- **{issue['criterion']}**: {issue['message']}\n"
                output += f"  - Suggestion: {issue['suggestion']}\n\n"

        if info:
            output += "### Info (Consider)\n\n"
            for issue in info:
                output += f"- **{issue['criterion']}**: {issue['message']}\n"
                output += f"  - Suggestion: {issue['suggestion']}\n\n"

        return output

    def can_handle(self, task: str) -> bool:
        """Check if this agent can handle the task."""
        review_keywords = [
            "review", "check", "analyze", "audit",
            "inspect", "evaluate", "assess", "verify",
        ]
        task_lower = task.lower()
        return any(kw in task_lower for kw in review_keywords)
