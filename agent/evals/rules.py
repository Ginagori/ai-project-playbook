"""
Evaluation Rules

Rule-based checks for artifact quality. Each rule returns a CheckResult.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CheckResult:
    """Result of a single quality check."""
    name: str
    passed: bool
    severity: str  # "critical", "warning", "info"
    message: str
    score: float = 1.0  # 0.0 = failed, 1.0 = passed, partial values allowed


# =============================================================================
# CLAUDE.md Rules
# =============================================================================

def has_required_sections(content: str, artifact_type: str = "claude_md") -> CheckResult:
    """Check that required sections are present."""
    section_map = {
        "claude_md": [
            ("Core Principles", "critical"),
            ("Tech Stack", "critical"),
            ("Architecture", "critical"),
            ("Code Style", "warning"),
            ("Testing", "warning"),
            ("Common Patterns", "info"),
        ],
        "prd": [
            ("Executive Summary", "critical"),
            ("Mission", "warning"),
            ("MVP Scope", "critical"),
            ("Success Criteria", "critical"),
            ("Tech Stack", "warning"),
        ],
        "plan": [
            ("Files to create", "critical"),
            ("Tasks", "critical"),
            ("Validation", "warning"),
        ],
        "prp": [
            ("Goal", "critical"),
            ("Success Criteria", "critical"),
            ("Implementation Blueprint", "critical"),
            ("Pseudocode", "critical"),
            ("Validation Loop", "critical"),
            ("Integration Points", "warning"),
            ("Anti-Patterns", "warning"),
            ("Must-Read Files", "info"),
        ],
    }

    required = section_map.get(artifact_type, section_map["claude_md"])
    content_lower = content.lower()

    missing_critical = []
    missing_warning = []
    missing_info = []
    found = 0

    for section_name, severity in required:
        # Check for heading or bold section
        patterns = [
            f"## {section_name.lower()}",
            f"### {section_name.lower()}",
            f"**{section_name.lower()}**",
            section_name.lower().replace(" ", "_"),
        ]
        section_found = any(p in content_lower for p in patterns)

        if section_found:
            found += 1
        else:
            if severity == "critical":
                missing_critical.append(section_name)
            elif severity == "warning":
                missing_warning.append(section_name)
            else:
                missing_info.append(section_name)

    total = len(required)
    score = found / total if total > 0 else 0.0
    passed = len(missing_critical) == 0

    missing_parts = []
    if missing_critical:
        missing_parts.append(f"CRITICAL missing: {', '.join(missing_critical)}")
    if missing_warning:
        missing_parts.append(f"Warning missing: {', '.join(missing_warning)}")
    if missing_info:
        missing_parts.append(f"Info missing: {', '.join(missing_info)}")

    message = (
        f"Found {found}/{total} sections."
        + (f" {'; '.join(missing_parts)}" if missing_parts else " All sections present.")
    )

    return CheckResult(
        name="has_required_sections",
        passed=passed,
        severity="critical" if missing_critical else ("warning" if missing_warning else "info"),
        message=message,
        score=score,
    )


def no_placeholder_text(content: str) -> CheckResult:
    """Check for placeholder/template text that wasn't filled in."""
    placeholders = [
        r"\[TODO\]",
        r"\[PLACEHOLDER\]",
        r"\[INSERT\s",
        r"\[YOUR\s",
        r"\[FILL\s",
        r"<your[\-_\s]",
        r"xxx",
        r"TBD",
        r"FIXME",
        r"lorem ipsum",
        r"example\.com",
    ]

    found_placeholders = []
    for pattern in placeholders:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            found_placeholders.extend(matches[:2])  # Limit to 2 examples per pattern

    passed = len(found_placeholders) == 0
    message = (
        "No placeholder text found."
        if passed
        else f"Found {len(found_placeholders)} placeholder(s): {', '.join(found_placeholders[:5])}"
    )

    return CheckResult(
        name="no_placeholder_text",
        passed=passed,
        severity="warning",
        message=message,
        score=1.0 if passed else 0.3,
    )


def has_tech_stack_specifics(content: str) -> CheckResult:
    """Check that tech stack mentions specific technologies, not generic terms."""
    generic_terms = ["N/A", "not set", "TBD", "to be decided", "any"]
    specific_techs = [
        "react", "next", "vue", "angular", "svelte",
        "fastapi", "express", "django", "flask", "nest",
        "postgresql", "supabase", "mongodb", "mysql", "sqlite", "firebase",
        "python", "typescript", "javascript", "rust", "go",
        "docker", "kubernetes", "railway", "vercel", "netlify",
        "pydantic", "langraph", "langgraph", "langchain",
        "stripe", "auth0", "clerk",
    ]

    content_lower = content.lower()

    # Check if there's a tech stack section
    has_section = any(
        term in content_lower
        for term in ["tech stack", "technology", "## stack"]
    )

    if not has_section:
        return CheckResult(
            name="has_tech_stack_specifics",
            passed=False,
            severity="critical",
            message="No tech stack section found.",
            score=0.0,
        )

    # Count specific vs generic mentions
    specific_found = [t for t in specific_techs if t in content_lower]
    generic_found = [t for t in generic_terms if t in content_lower]

    score = min(len(specific_found) / 3, 1.0)  # At least 3 specific techs for full score
    passed = len(specific_found) >= 2 and len(generic_found) <= 1

    message = (
        f"Found {len(specific_found)} specific technologies: {', '.join(specific_found[:5])}."
        + (f" Generic terms: {', '.join(generic_found)}" if generic_found else "")
    )

    return CheckResult(
        name="has_tech_stack_specifics",
        passed=passed,
        severity="warning" if not passed else "info",
        message=message,
        score=score,
    )


def has_validation_commands(content: str) -> CheckResult:
    """Check that the artifact includes validation/testing commands."""
    validation_patterns = [
        r"pytest",
        r"npm\s+test",
        r"npm\s+run\s+(?:lint|test|build)",
        r"vitest",
        r"ruff",
        r"mypy",
        r"pyright",
        r"tsc\s+--noEmit",
        r"eslint",
        r"prettier",
        r"```bash",
        r"```sh",
        r"docker\s+(?:build|run|compose)",
        r"kubectl",
        r"curl\s+",
    ]

    content_lower = content.lower()
    found_commands = []
    for pattern in validation_patterns:
        if re.search(pattern, content_lower):
            found_commands.append(pattern.replace(r"\s+", " ").replace(r"(?:", "("))

    passed = len(found_commands) >= 2
    score = min(len(found_commands) / 3, 1.0)

    message = (
        f"Found {len(found_commands)} validation commands."
        if passed
        else f"Only {len(found_commands)} validation command(s) found. Add more testing/linting commands."
    )

    return CheckResult(
        name="has_validation_commands",
        passed=passed,
        severity="warning",
        message=message,
        score=score,
    )


def has_file_references(content: str) -> CheckResult:
    """Check that the artifact references specific files/paths."""
    # Match file paths like src/auth/router.py, components/Dashboard.tsx, etc.
    file_patterns = [
        r"[a-zA-Z_/]+\.[a-zA-Z]{2,4}",  # file.ext
        r"src/[a-zA-Z_/]+",               # src/...
        r"tests?/[a-zA-Z_/]+",            # test(s)/...
        r"`[a-zA-Z_./-]+\.[a-zA-Z]{2,4}`", # `file.ext` in backticks
    ]

    all_matches = set()
    for pattern in file_patterns:
        matches = re.findall(pattern, content)
        all_matches.update(m for m in matches if len(m) > 5 and "/" in m or "." in m)

    # Filter out false positives
    real_files = [
        m for m in all_matches
        if not m.startswith("http") and not m.startswith("www")
        and any(m.endswith(ext) for ext in [".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".yaml", ".yml", ".toml", ".json", ".sql", ".css", ".html", ".env", ".sh"])
    ]

    count = len(real_files)
    passed = count >= 3
    score = min(count / 5, 1.0)

    message = (
        f"Found {count} file references."
        if passed
        else f"Only {count} file reference(s). Plans should reference specific files."
    )

    return CheckResult(
        name="has_file_references",
        passed=passed,
        severity="warning" if not passed else "info",
        message=message,
        score=score,
    )


def minimum_length(content: str, min_chars: int = 500, artifact_type: str = "claude_md") -> CheckResult:
    """Check that the artifact meets minimum length requirements."""
    length_map = {
        "claude_md": 800,
        "prd": 600,
        "plan": 300,
        "prp": 1000,
    }

    min_required = length_map.get(artifact_type, min_chars)
    actual = len(content.strip())

    passed = actual >= min_required
    score = min(actual / min_required, 1.0) if min_required > 0 else 1.0

    message = (
        f"Length: {actual} chars (minimum: {min_required})."
        if passed
        else f"Too short: {actual} chars (minimum: {min_required}). Add more detail."
    )

    return CheckResult(
        name="minimum_length",
        passed=passed,
        severity="critical" if actual < min_required * 0.5 else "warning",
        message=message,
        score=score,
    )


def has_success_criteria(content: str) -> CheckResult:
    """Check that the artifact includes measurable success criteria."""
    criteria_patterns = [
        r"success\s+criteria",
        r"\[\s*[xX ]\s*\]",      # Checkbox items
        r"- \[ \]",               # Markdown checkboxes
        r"must\s+(?:be|have|support)",
        r"should\s+(?:be|have|support)",
        r"acceptance\s+criteria",
        r"definition\s+of\s+done",
        r"requirements?:",
        r"(?:80|90|95|99|100)\s*%",  # Percentage targets
    ]

    content_lower = content.lower()
    found = []
    for pattern in criteria_patterns:
        if re.search(pattern, content_lower):
            found.append(pattern)

    passed = len(found) >= 2
    score = min(len(found) / 3, 1.0)

    message = (
        f"Found {len(found)} success criteria indicators."
        if passed
        else "Missing clear success criteria. Add measurable outcomes."
    )

    return CheckResult(
        name="has_success_criteria",
        passed=passed,
        severity="warning",
        message=message,
        score=score,
    )


def has_feature_prioritization(content: str) -> CheckResult:
    """Check that features are prioritized (P0/P1/P2 or similar)."""
    priority_patterns = [
        r"P0\b",
        r"P1\b",
        r"P2\b",
        r"(?:high|medium|low)\s+priority",
        r"(?:must|should|could|won't)\s+have",
        r"MoSCoW",
        r"Core\s+Features?",
        r"Nice[\s-]to[\s-]Have",
        r"MVP\s+Scope",
        r"Phase\s+[12345]",
        r"Sprint\s+[12345]",
        r"\b(?:critical|important|optional)\b",
    ]

    content_lower = content.lower()
    found = []
    for pattern in priority_patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            found.append(pattern)

    passed = len(found) >= 2
    score = min(len(found) / 3, 1.0)

    message = (
        f"Found {len(found)} prioritization indicators."
        if passed
        else "Missing feature prioritization. Add P0/P1 or priority levels."
    )

    return CheckResult(
        name="has_feature_prioritization",
        passed=passed,
        severity="warning",
        message=message,
        score=score,
    )


# =============================================================================
# Additional rules for specific artifact types
# =============================================================================

def has_code_examples(content: str) -> CheckResult:
    """Check that CLAUDE.md includes code examples/patterns."""
    code_blocks = re.findall(r"```(?:python|typescript|javascript|sql|bash|yaml|json)", content.lower())
    count = len(code_blocks)

    passed = count >= 2
    score = min(count / 3, 1.0)

    message = (
        f"Found {count} code examples."
        if passed
        else f"Only {count} code example(s). CLAUDE.md should include common patterns."
    )

    return CheckResult(
        name="has_code_examples",
        passed=passed,
        severity="info",
        message=message,
        score=score,
    )


def has_architecture_pattern(content: str) -> CheckResult:
    """Check that a specific architecture pattern is mentioned."""
    patterns = [
        "vertical slice",
        "three-layer",
        "clean architecture",
        "hexagonal",
        "microservices",
        "monolith",
        "mvc",
        "mvvm",
        "event-driven",
        "cqrs",
        "serverless",
        "plugin architecture",
    ]

    content_lower = content.lower()
    found = [p for p in patterns if p in content_lower]

    passed = len(found) >= 1
    score = 1.0 if passed else 0.0

    message = (
        f"Architecture pattern(s): {', '.join(found)}"
        if passed
        else "No architecture pattern specified. Choose one: Vertical Slice, Clean Architecture, etc."
    )

    return CheckResult(
        name="has_architecture_pattern",
        passed=passed,
        severity="warning",
        message=message,
        score=score,
    )


def has_integration_points(content: str) -> CheckResult:
    """Check that feature plans mention integration points."""
    integration_patterns = [
        r"integrat(?:e|ion|es)",
        r"connect(?:s|ion)?\s+(?:to|with)",
        r"depends?\s+on",
        r"import(?:s|ed)?\s+from",
        r"calls?\s+(?:to|the)",
        r"API\s+(?:call|endpoint|request)",
        r"database\s+(?:query|table|migration)",
        r"auth(?:entication|orization)",
    ]

    content_lower = content.lower()
    found = [p for p in integration_patterns if re.search(p, content_lower)]

    passed = len(found) >= 1
    score = min(len(found) / 2, 1.0)

    message = (
        f"Found {len(found)} integration references."
        if passed
        else "No integration points mentioned. Plans should describe how this feature connects to others."
    )

    return CheckResult(
        name="has_integration_points",
        passed=passed,
        severity="info",
        message=message,
        score=score,
    )


# =============================================================================
# PRP-Specific Rules
# =============================================================================

def has_dependency_declarations(content: str) -> CheckResult:
    """Check that PRP tasks declare their dependencies."""
    dep_patterns = [
        r"depends?\s+on",
        r"required?\s+by",
        r"after\s+(?:completing|implementing)",
        r"prerequisite",
        r"blocked\s+by",
        r"\bdependenc(?:y|ies)\b",
    ]

    content_lower = content.lower()
    found = [p for p in dep_patterns if re.search(p, content_lower)]

    passed = len(found) >= 1
    score = min(len(found) / 2, 1.0)

    message = (
        f"Found {len(found)} dependency declarations."
        if passed
        else "No dependency declarations. PRP should specify what must be built first."
    )

    return CheckResult(
        name="has_dependency_declarations",
        passed=passed,
        severity="warning",
        message=message,
        score=score,
    )


def has_specific_file_paths(content: str) -> CheckResult:
    """Check that file paths are specific (not generic placeholders)."""
    # Match paths like src/auth/router.py, src/models/user.ts
    specific_paths = re.findall(r"src/[a-zA-Z_]+/[a-zA-Z_]+\.[a-zA-Z]{2,4}", content)
    # Match test paths
    test_paths = re.findall(r"tests?/[a-zA-Z_]+/[a-zA-Z_]+\.[a-zA-Z]{2,4}", content)
    # Match migration paths
    migration_paths = re.findall(r"migrations?/[a-zA-Z_0-9]+\.[a-zA-Z]{2,4}", content)

    total = len(specific_paths) + len(test_paths) + len(migration_paths)
    passed = total >= 3
    score = min(total / 5, 1.0)

    message = (
        f"Found {total} specific file paths ({len(specific_paths)} src, {len(test_paths)} test, {len(migration_paths)} migration)."
        if passed
        else f"Only {total} specific file path(s). PRP should reference exact files to create/modify."
    )

    return CheckResult(
        name="has_specific_file_paths",
        passed=passed,
        severity="warning" if not passed else "info",
        message=message,
        score=score,
    )


def has_pseudocode(content: str) -> CheckResult:
    """Check that PRP includes pseudocode or code examples."""
    code_blocks = re.findall(r"```(?:python|typescript|javascript|sql|bash)", content.lower())
    has_class = bool(re.search(r"class\s+\w+", content))
    has_function = bool(re.search(r"(?:def|async def|function|const)\s+\w+", content))

    indicators = len(code_blocks) + (1 if has_class else 0) + (1 if has_function else 0)
    passed = indicators >= 2
    score = min(indicators / 3, 1.0)

    message = (
        f"Found {len(code_blocks)} code blocks with classes/functions."
        if passed
        else "Missing pseudocode. PRP should include implementation code examples."
    )

    return CheckResult(
        name="has_pseudocode",
        passed=passed,
        severity="critical" if indicators == 0 else "warning",
        message=message,
        score=score,
    )
