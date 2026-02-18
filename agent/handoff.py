"""
Handoff Writer — Write project artifacts to disk for autonomous implementation.

Creates a structured file layout that Claude Code can read from disk,
eliminating reliance on in-memory context and preventing hallucination.

Usage:
    writer = HandoffWriter(project, "/path/to/project")
    error = writer.validate()
    if error:
        print(error)
    else:
        writer.write_all()
        print(writer.format_report())
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from agent.models.project import Feature, ProjectState
from agent.prp_builder import PRPBuilder
from agent.tools.file_operations import FileResult, write_file, ensure_directory


class HandoffWriter:
    """
    Writes all project artifacts to disk for Claude Code handoff.

    The Playbook agent is the PM — it plans, designs, and structures.
    Claude Code is the engineer — it reads the plan from disk and executes.

    This class bridges the two by writing:
    - CLAUDE.md (project rules)
    - docs/PRD.md (requirements)
    - docs/ROADMAP.md (feature order + dependencies)
    - .playbook/handoff.md (anti-hallucination execution protocol)
    - .playbook/session.json (machine-readable metadata)
    - .playbook/prps/*.md (one PRP per feature)
    """

    def __init__(self, project: ProjectState, project_path: str):
        self.project = project
        self.project_path = Path(project_path)
        self.prp_builder = PRPBuilder(project)
        self.ordered_features = self.prp_builder._topological_sort_features()
        self.results: list[FileResult] = []

    def validate(self) -> str | None:
        """Validate preconditions. Returns error message or None if valid."""
        if not self.project_path.exists():
            return f"Project path does not exist: {self.project_path}"
        if not self.project_path.is_dir():
            return f"Project path is not a directory: {self.project_path}"
        if not self.project.claude_md:
            return "CLAUDE.md has not been generated. Complete the Planning phase first."
        if not self.project.prd:
            return "PRD has not been generated. Complete the Planning phase first."
        if not self.project.features:
            return "No features defined. Complete the Roadmap phase first."
        return None

    def write_all(
        self,
        overwrite_claude_md: bool = False,
        write_prps: bool = True,
    ) -> list[FileResult]:
        """Write all artifacts to disk. Returns list of FileResult."""
        self.results = []

        # 1. CLAUDE.md — skip if exists unless explicitly overwriting
        self._write_claude_md(overwrite_claude_md)

        # 2. docs/PRD.md
        self._write_prd()

        # 3. docs/ROADMAP.md
        self._write_roadmap()

        # 4. .playbook/session.json
        self._write_session_json()

        # 5. .playbook/handoff.md
        self._write_handoff()

        # 6. .playbook/prps/*.md
        if write_prps:
            self._write_prps()

        return self.results

    # =========================================================================
    # File Writers
    # =========================================================================

    def _write_claude_md(self, overwrite: bool) -> None:
        path = str(self.project_path / "CLAUDE.md")
        result = write_file(path, self.project.claude_md, overwrite=overwrite)
        self.results.append(result)

    def _write_prd(self) -> None:
        ensure_directory(self.project_path / "docs")
        path = str(self.project_path / "docs" / "PRD.md")
        result = write_file(path, self.project.prd, overwrite=True)
        self.results.append(result)

    def _write_roadmap(self) -> None:
        ensure_directory(self.project_path / "docs")
        content = self._generate_roadmap_md()
        path = str(self.project_path / "docs" / "ROADMAP.md")
        result = write_file(path, content, overwrite=True)
        self.results.append(result)

    def _write_session_json(self) -> None:
        ensure_directory(self.project_path / ".playbook")
        data = {
            "session_id": self.project.id,
            "objective": self.project.objective,
            "project_type": self.project.project_type.value if self.project.project_type else None,
            "scale": self.project.scale.value,
            "current_phase": self.project.current_phase.value,
            "mode": self.project.mode.value,
            "tech_stack": {
                "frontend": self.project.tech_stack.frontend,
                "backend": self.project.tech_stack.backend,
                "database": self.project.tech_stack.database,
                "auth": self.project.tech_stack.auth,
                "deployment": self.project.tech_stack.deployment,
            },
            "features": [
                {
                    "name": f.name,
                    "description": f.description,
                    "priority": f.priority,
                    "status": f.status,
                    "depends_on": f.depends_on,
                    "success_criteria": f.success_criteria,
                }
                for f in self.ordered_features
            ],
            "total_features": len(self.ordered_features),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "playbook_version": "1.0",
        }
        content = json.dumps(data, indent=2, ensure_ascii=False)
        path = str(self.project_path / ".playbook" / "session.json")
        result = write_file(path, content, overwrite=True)
        self.results.append(result)

    def _write_handoff(self) -> None:
        ensure_directory(self.project_path / ".playbook")
        content = self._generate_handoff_md()
        path = str(self.project_path / ".playbook" / "handoff.md")
        result = write_file(path, content, overwrite=True)
        self.results.append(result)

    def _write_prps(self) -> None:
        prps_dir = self.project_path / ".playbook" / "prps"
        ensure_directory(prps_dir)
        for i, feature in enumerate(self.ordered_features, 1):
            slug = self._feature_slug(feature.name)
            filename = f"{i:02d}-{slug}.md"
            content = self.prp_builder.build_feature_prp(feature)
            path = str(prps_dir / filename)
            result = write_file(path, content, overwrite=True)
            self.results.append(result)

    # =========================================================================
    # Content Generators
    # =========================================================================

    def _generate_roadmap_md(self) -> str:
        """Generate ROADMAP.md from topologically sorted features."""
        p = self.project
        lines = [
            f"# Implementation Roadmap: {p.objective}",
            "",
            f"> **Project Type:** {p.project_type.value if p.project_type else 'N/A'}",
            f"> **Scale:** {p.scale.value}",
            f"> **Total Features:** {len(self.ordered_features)}",
            "",
            "---",
            "",
            "## Feature Execution Order",
            "",
            "Execute features in this exact order. Do NOT skip dependencies.",
            "",
            "| # | Feature | Priority | Depends On | Status |",
            "|---|---------|----------|------------|--------|",
        ]

        for i, feature in enumerate(self.ordered_features, 1):
            deps = ", ".join(feature.depends_on) if feature.depends_on else "-"
            lines.append(
                f"| {i} | {feature.name} | {feature.priority.upper()} | {deps} | {feature.status} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Dependency Graph",
            "",
            self.prp_builder._build_dependency_graph(),
            "",
            "---",
            "",
            "## Feature Details",
            "",
        ])

        for i, feature in enumerate(self.ordered_features, 1):
            slug = self._feature_slug(feature.name)
            lines.append(f"### {i}. {feature.name}")
            lines.append(f"**Description:** {feature.description}")
            lines.append(f"**Priority:** {feature.priority.upper()}")
            if feature.depends_on:
                lines.append(f"**Depends on:** {', '.join(feature.depends_on)}")
            if feature.success_criteria:
                lines.append("**Success Criteria:**")
                for c in feature.success_criteria:
                    lines.append(f"- [ ] {c}")
            lines.append(f"**PRP:** `.playbook/prps/{i:02d}-{slug}.md`")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## Execution Notes",
            "",
            "- Execute features **in the order listed** above.",
            "- Do NOT skip dependencies. Each feature builds on its predecessors.",
            "- Run validation after each feature before proceeding to the next.",
            "- Refer to each feature's PRP file for detailed implementation instructions.",
            "",
            f"*Generated by AI Project Playbook on {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        ])

        return "\n".join(lines)

    def _generate_handoff_md(self) -> str:
        """Generate the anti-hallucination handoff protocol."""
        session_id = self.project.id
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        total = len(self.ordered_features)

        # Build feature execution list
        feature_list_lines = []
        for i, feature in enumerate(self.ordered_features, 1):
            slug = self._feature_slug(feature.name)
            deps = f" (depends on: {', '.join(feature.depends_on)})" if feature.depends_on else ""
            feature_list_lines.append(
                f"{i}. **{feature.name}**{deps} — `.playbook/prps/{i:02d}-{slug}.md`"
            )
        feature_list = "\n".join(feature_list_lines)

        return f"""# Handoff Protocol

> Generated by AI Project Playbook. This file is auto-generated — do not edit manually.
> Session: `{session_id}` | Generated: {timestamp}

---

## What Is This?

The Playbook agent (your PM) has completed the planning phase for this project.
Everything you need to implement is documented in this directory:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project rules, architecture, code style, conventions |
| `docs/PRD.md` | Complete product requirements |
| `docs/ROADMAP.md` | Feature execution order with dependencies |
| `.playbook/session.json` | Machine-readable session metadata |
| `.playbook/prps/*.md` | Per-feature implementation specs (PRPs) |

Your job: **read the plan, follow it exactly, and implement.**

---

## Rules for Claude Code

### Anti-Hallucination Protocol

1. **Read before acting.** Before implementing ANY feature, read these files FROM DISK:
   - `CLAUDE.md` — project rules, architecture, code style
   - `docs/PRD.md` — full product requirements
   - `docs/ROADMAP.md` — feature order and dependencies
   - The PRP file for the current feature (`.playbook/prps/NN-feature-name.md`)

2. **Do NOT guess file contents.** If you cannot read a file, STOP and tell the user.
   Never reconstruct file contents from memory. Always use the Read tool.

3. **Follow CLAUDE.md patterns exactly.** Do not invent new patterns, naming conventions,
   or architectural layers. If CLAUDE.md specifies a pattern, use it. No improvisation.

4. **No placeholders, no TODOs.** Every function must be fully implemented.
   Every file must be complete. "Implement later" is not acceptable output.

5. **When stuck, ask.** Do not fabricate solutions. If you are uncertain about
   a requirement, a dependency, or an approach, STOP and ask the user.
   State: what you know, what you don't know, and what you need to proceed.

6. **One feature at a time.** Do not work on multiple features simultaneously.
   Complete one, validate it, get approval, then proceed to the next.

---

## Execution Protocol

### Startup Sequence

```
Step 1: Read CLAUDE.md              (understand project rules)
Step 2: Read docs/PRD.md            (understand what to build)
Step 3: Read docs/ROADMAP.md        (understand the order)
Step 4: Start Feature 1             (read its PRP, implement, validate)
```

### Per-Feature Loop

For each feature in the order listed below:

```
1. Read .playbook/prps/NN-feature-name.md    (the PRP for this feature)
2. Implement the feature following the PRP:
   - Create the files listed in "Files to Create"
   - Follow the pseudocode structure
   - Use the patterns from CLAUDE.md
3. Run the validation commands from the PRP:
   - Lint, type check, unit tests, integration tests
4. Verify all success criteria from the PRP pass
5. Commit with conventional commit message: feat: feature-name
6. Report checkpoint status to user
7. Wait for "approved" before proceeding
```

---

## Feature Execution Order

{feature_list}

**Total:** {total} features

---

## Checkpoint Protocol

After completing EACH feature, verify:

- [ ] All files listed in the PRP's "Files to Create" exist
- [ ] All validation commands from the PRP pass (lint, types, tests)
- [ ] No TODOs, placeholder code, or incomplete implementations remain
- [ ] Integration with previously completed features works correctly
- [ ] Changes committed with `feat: feature-name` message

**Report checkpoint status to the user and wait for "approved" to continue.**

---

## When Something Fails

1. Read the error message carefully
2. Re-read the relevant PRP section
3. Check if the issue is a missing dependency (check `docs/ROADMAP.md`)
4. If you cannot resolve it in 2 attempts, **STOP and ask the user**
   - Include: the error, what you tried, and what you think the root cause is
   - Do NOT try creative workarounds without user approval

---

## Final Validation

After all features are complete:

1. Run the full project validation suite (lint, types, all tests, build)
2. Verify all features from `docs/ROADMAP.md` have status "completed"
3. Report final status to the user

---

*This handoff was generated by AI Project Playbook v1.0*
*Session: `{session_id}` | Features: {total} | Generated: {timestamp}*
"""

    # =========================================================================
    # Utilities
    # =========================================================================

    @staticmethod
    def _feature_slug(name: str) -> str:
        """Convert feature name to a filesystem-safe slug."""
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def format_report(self) -> str:
        """Format write results as a markdown report for the user."""
        written = [r for r in self.results if r.success]
        skipped = [r for r in self.results if not r.success and "already exists" in r.message]
        failed = [r for r in self.results if not r.success and "already exists" not in r.message]

        lines = [
            "## Handoff Complete",
            "",
            f"**Project:** {self.project.objective}",
            f"**Session:** `{self.project.id}`",
            f"**Path:** `{self.project_path}`",
            f"**Features:** {len(self.ordered_features)}",
            "",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| Written | {len(written)} |",
            f"| Skipped | {len(skipped)} |",
            f"| Failed | {len(failed)} |",
            "",
        ]

        if written:
            lines.append("### Files Written")
            for r in written:
                # Show relative path from project root
                try:
                    rel = Path(r.path).relative_to(self.project_path)
                except ValueError:
                    rel = r.path
                lines.append(f"- `{rel}`")
            lines.append("")

        if skipped:
            lines.append("### Files Skipped (already exist)")
            for r in skipped:
                try:
                    rel = Path(r.path).relative_to(self.project_path)
                except ValueError:
                    rel = r.path
                lines.append(f"- `{rel}` — {r.message}")
            lines.append("")
            lines.append("> To overwrite CLAUDE.md, re-run with `overwrite_claude_md=True`")
            lines.append("")

        if failed:
            lines.append("### Files Failed")
            for r in failed:
                lines.append(f"- `{r.path}` — {r.message}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "### Next Steps",
            "",
            "1. Open the project directory in Claude Code",
            "2. Tell Claude Code: **Read `.playbook/handoff.md` and follow the execution protocol**",
            "3. Claude Code will read each file from disk and implement feature by feature",
            "4. Review and approve each checkpoint before Claude Code continues",
        ])

        return "\n".join(lines)
