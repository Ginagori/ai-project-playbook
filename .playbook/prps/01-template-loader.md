# PRP: Template Loader

## Goal
Create a module that loads markdown templates from `playbook/templates/` and provides them as structured skeletons for artifact generation — so the Playbook never generates an artifact without first reading its official template.

## Why
Today `_generate_claude_md()`, `_generate_prd()`, and `PRPBuilder.build_feature_prp()` all use hardcoded string templates embedded in Python code. The real templates in `playbook/templates/` (PRP: 160 lines, PRD: 655 lines, Plan: 552 lines) are never loaded. This means:
- Generated artifacts miss 80% of the template's sections
- Template improvements require code changes, not just markdown edits
- The user's explicit lesson ("ALWAYS read the corresponding template FIRST") is violated

## What
A `TemplateLoader` class that:
1. Loads any template from `playbook/templates/` by name
2. Parses it into sections (using the existing `_parse_markdown_sections` helper)
3. Returns both raw content and parsed structure
4. Caches loaded templates (they don't change at runtime)
5. Provides a `get_section_names()` method so generators know which sections to fill

## Success Criteria
- [ ] `TemplateLoader("prp-template").sections` returns all PRP sections (Goal, Why, What, Success Criteria, Context, Implementation Blueprint, Validation Loop, Final Validation Checklist, Anti-Patterns)
- [ ] `TemplateLoader("prd-template").raw` returns the full 655-line PRD template
- [ ] Templates are loaded from disk on first access, cached after
- [ ] If a template file doesn't exist, raises a clear error (not silent failure)
- [ ] Existing code (`_generate_claude_md`, `_generate_prd`, `PRPBuilder`) is NOT broken (this is additive)

## Context

### Must-Read Files
- `playbook/templates/prp-template.md` — PRP structure to preserve
- `playbook/templates/prd-template.md` — PRD structure (655 lines)
- `playbook/templates/plan-template.md` — Plan structure (552 lines)
- `agent/prp_builder.py:22-41` — existing `_parse_markdown_sections()` helper

### Codebase Context
- `_parse_markdown_sections()` already exists in `prp_builder.py` and works well
- `PLAYBOOK_DIR` is already defined in `playbook_rag.py` and `playbook_mcp.py`
- The templates use standard markdown headers (## and ###)

### Known Gotchas
- Templates contain code blocks with `#` inside them — the section parser must only match lines that START with `#`, not `#` inside fenced code blocks
- The PRP template wraps its actual template in a ```markdown fence — the loader must extract content inside the fence
- Windows paths: use `Path` objects, not string concatenation

### Relevant Patterns
- Follow the existing singleton pattern used by `get_lessons_db()` in `agent/meta_learning/models.py`
- Use `Path(__file__)` relative resolution like `PLAYBOOK_DIR` in `playbook_rag.py`

## Implementation Blueprint

### Files to Create
- `agent/template_loader.py` — the TemplateLoader module

### Files to Modify
- (none — this is additive, consumers will be modified in later PRPs)

### Data Model
```python
@dataclass
class TemplateSection:
    """A parsed section from a template."""
    name: str          # e.g., "Goal", "Success Criteria"
    level: int         # heading level (1, 2, 3)
    content: str       # raw content under this heading
    subsections: list[str]  # names of child subsections
```

### Tasks

#### Task 1: Create TemplateLoader class
**Files:** `agent/template_loader.py`
**Pseudocode:**
```python
from pathlib import Path
from dataclasses import dataclass, field

TEMPLATES_DIR = Path(__file__).parent.parent / "playbook" / "templates"

@dataclass
class TemplateSection:
    name: str
    level: int
    content: str
    subsections: list[str] = field(default_factory=list)

class TemplateLoader:
    """Loads and parses markdown templates from playbook/templates/."""

    _cache: dict[str, "TemplateLoader"] = {}  # class-level cache

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
        # Try with and without .md extension
        path = TEMPLATES_DIR / f"{self.template_name}.md"
        if not path.exists():
            path = TEMPLATES_DIR / self.template_name
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_name} in {TEMPLATES_DIR}")

        self._raw = path.read_text(encoding="utf-8")
        self._sections = self._parse_sections(self._raw)

    @property
    def raw(self) -> str:
        """Full raw template content."""
        if self._raw is None:
            self._load()
        return self._raw

    @property
    def sections(self) -> dict[str, TemplateSection]:
        """Parsed sections dict."""
        if self._sections is None:
            self._load()
        return self._sections

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
    def _parse_sections(content: str) -> dict[str, TemplateSection]:
        """Parse markdown into sections, respecting code fences."""
        sections: dict[str, TemplateSection] = {}
        current_name = ""
        current_level = 0
        current_lines: list[str] = []
        in_code_fence = False

        for line in content.split("\n"):
            # Track code fence state
            if line.strip().startswith("```"):
                in_code_fence = not in_code_fence
                current_lines.append(line)
                continue

            # Only match headers outside code fences
            if not in_code_fence and line.startswith("#"):
                # Save previous section
                if current_name:
                    sections[current_name] = TemplateSection(
                        name=current_name,
                        level=current_level,
                        content="\n".join(current_lines).strip(),
                        subsections=[],
                    )

                # Parse new header
                hashes = len(line) - len(line.lstrip("#"))
                current_name = line.lstrip("#").strip()
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
```

### Integration Points
- **Called by:** `orchestrator.py` (planning_node, implementation_node), `prp_builder.py`
- **Depends on:** `playbook/templates/` directory existing with .md files
- **No external dependencies** — pure file I/O + parsing

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check agent/template_loader.py --fix
ruff format agent/template_loader.py
```

### Level 2: Type Safety
```bash
mypy agent/template_loader.py --ignore-missing-imports
```

### Level 3: Unit Tests
```python
# Test inline — run with:
# .venv/Scripts/python.exe -c "..."
from agent.template_loader import TemplateLoader

# Test PRP template loads
loader = TemplateLoader.get("prp-template")
assert "goal" in [s.lower() for s in loader.get_section_names()]
assert "success criteria" in [s.lower() for s in loader.get_section_names()]
assert "anti-patterns" in [s.lower() for s in loader.get_section_names()]
print(f"PRP sections: {loader.get_section_names()}")

# Test PRD template loads
prd = TemplateLoader.get("prd-template")
assert len(prd.raw) > 1000  # 655-line template
print(f"PRD raw length: {len(prd.raw)}")

# Test caching
loader2 = TemplateLoader.get("prp-template")
assert loader is loader2  # same object

# Test missing template
try:
    TemplateLoader.get("nonexistent")
    assert False, "Should have raised"
except FileNotFoundError:
    pass

print("All template loader tests passed!")
```

### Level 4: Integration Tests
```bash
.venv/Scripts/python.exe -c "
from agent.template_loader import TemplateLoader
# Verify all 5 templates load
for name in ['prp-template', 'prd-template', 'plan-template', 'code-review', 'validate-command']:
    t = TemplateLoader.get(name)
    print(f'{name}: {len(t.sections)} sections, {len(t.raw)} chars')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from agent.template_loader import TemplateLoader; print('Import OK')"
```

## Final Validation Checklist
- [ ] All 5 templates load successfully
- [ ] Section parser handles code fences correctly (no false header matches)
- [ ] Cache works (same object returned for same template name)
- [ ] FileNotFoundError for missing templates
- [ ] No changes to existing code (purely additive)

## Anti-Patterns
- Do NOT read templates at module import time (lazy load on first access)
- Do NOT parse with regex that matches `#` inside code blocks
- Do NOT hardcode template section names — discover them from the file
- Do NOT modify any existing files in this PRP
