"""
Template Loader — Load and parse markdown templates from playbook/templates/.

Provides structured access to template sections so artifact generators
can follow the official template structure instead of hardcoding formats.
"""

from dataclasses import dataclass, field
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent.parent / "playbook" / "templates"


@dataclass
class TemplateSection:
    """A parsed section from a template."""

    name: str  # e.g., "Goal", "Success Criteria"
    level: int  # heading level (1, 2, 3)
    content: str  # raw content under this heading
    subsections: list[str] = field(default_factory=list)


class TemplateLoader:
    """
    Loads and parses markdown templates from playbook/templates/.

    Usage:
        loader = TemplateLoader.get("prp-template")
        sections = loader.get_section_names()
        goal_section = loader.get_section("Goal")
    """

    _cache: dict[str, "TemplateLoader"] = {}

    def __init__(self, template_name: str):
        self.template_name = template_name
        self._raw: str | None = None
        self._sections: dict[str, TemplateSection] | None = None

    @classmethod
    def get(cls, template_name: str) -> "TemplateLoader":
        """Get a cached template loader (singleton per template)."""
        if template_name not in cls._cache:
            loader = cls(template_name)
            loader._load()
            cls._cache[template_name] = loader
        return cls._cache[template_name]

    def _load(self) -> None:
        """Load template from disk."""
        path = TEMPLATES_DIR / f"{self.template_name}.md"
        if not path.exists():
            path = TEMPLATES_DIR / self.template_name
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_name} in {TEMPLATES_DIR}")

        raw = path.read_text(encoding="utf-8")
        self._raw = raw
        # If the template wraps content in a ```markdown fence, extract it
        inner = self._extract_inner_template(raw)
        self._sections = self._parse_sections(inner)

    @property
    def raw(self) -> str:
        """Full raw template content."""
        if self._raw is None:
            self._load()
        return self._raw  # type: ignore[return-value]

    @property
    def sections(self) -> dict[str, TemplateSection]:
        """Parsed sections dict."""
        if self._sections is None:
            self._load()
        return self._sections  # type: ignore[return-value]

    def get_section_names(self) -> list[str]:
        """Get ordered list of section names."""
        return list(self.sections.keys())

    def get_section(self, name: str) -> TemplateSection | None:
        """Get a specific section by name (case-insensitive)."""
        name_lower = name.lower()
        for key, section in self.sections.items():
            if key.lower() == name_lower:
                return section
        return None

    @staticmethod
    def _extract_inner_template(content: str) -> str:
        """Extract template content from within a ```markdown fence if present.

        Some templates (like prp-template.md) wrap the actual template inside
        a ```markdown code fence. This method extracts that inner content and
        handles nested fences by tracking depth.
        """
        lines = content.split("\n")

        # Find ```markdown opening
        start_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("```markdown"):
                start_idx = i + 1
                break

        if start_idx is None:
            return content  # No markdown fence, return as-is

        # Find matching close — track nesting depth
        # ```python, ```bash, etc. = opening (depth++)
        # ``` alone = closing (depth--)
        depth = 1
        end_idx = len(lines)
        for i in range(start_idx, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("```") and len(stripped) > 3:
                # Opening fence with language spec (```python, ```bash, etc.)
                depth += 1
            elif stripped == "```":
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break

        return "\n".join(lines[start_idx:end_idx])

    @staticmethod
    def _parse_sections(content: str) -> dict[str, TemplateSection]:
        """Parse markdown into sections, respecting code fences."""
        sections: dict[str, TemplateSection] = {}
        current_name = ""
        current_level = 0
        current_lines: list[str] = []
        in_code_fence = False

        for line in content.split("\n"):
            stripped = line.strip()

            # Track code fence state
            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                current_lines.append(line)
                continue

            # Only match headers outside code fences
            if not in_code_fence and stripped.startswith("#"):
                # Save previous section
                if current_name:
                    sections[current_name] = TemplateSection(
                        name=current_name,
                        level=current_level,
                        content="\n".join(current_lines).strip(),
                        subsections=[],
                    )

                # Parse new header
                hashes = len(stripped) - len(stripped.lstrip("#"))
                current_name = stripped.lstrip("#").strip()
                current_level = hashes
                current_lines = []
            else:
                current_lines.append(line)

        # Save last section
        if current_name:
            sections[current_name] = TemplateSection(
                name=current_name,
                level=current_level,
                content="\n".join(current_lines).strip(),
                subsections=[],
            )

        # Compute subsections
        section_list = list(sections.values())
        for i, section in enumerate(section_list):
            for j in range(i + 1, len(section_list)):
                if section_list[j].level > section.level:
                    section.subsections.append(section_list[j].name)
                else:
                    break

        return sections

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the template cache (useful for testing)."""
        cls._cache.clear()
