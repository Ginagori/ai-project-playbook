# Agent Security & Safe Execution Guide

A comprehensive guide for securing AI agents that execute actions — fail-closed model, sandboxing, approval workflows, and process lifecycle management.

## The Core Principle

> **Fail-closed**: Block everything by default. Only explicitly allowed actions can execute.

Unlike traditional software where most operations are safe, agents can:
- Execute arbitrary code
- Access databases and APIs
- Send messages to users
- Modify files and configurations
- Make financial transactions

**Security is not optional.** Every agent that executes actions on behalf of users needs a security model.

---

## Fail-Closed Security Model

### Default Deny

```python
class ToolPermissions:
    """Fail-closed: only explicitly allowed tools can execute."""

    def __init__(self):
        self.allowlist: dict[str, set[str]] = {}  # channel -> allowed tools

    def is_allowed(self, channel: str, tool_name: str) -> bool:
        """Check if a tool is allowed in this channel. Not listed = blocked."""
        allowed = self.allowlist.get(channel, set())
        return tool_name in allowed  # Empty set = nothing allowed

    def grant(self, channel: str, tools: list[str]):
        """Explicitly grant tool access for a channel."""
        self.allowlist.setdefault(channel, set()).update(tools)

    def revoke(self, channel: str, tools: list[str]):
        """Remove tool access for a channel."""
        if channel in self.allowlist:
            self.allowlist[channel] -= set(tools)
```

### Per-Channel/User/Group Permissions

```python
class PermissionManager:
    """Hierarchical permission system: global < group < channel < user."""

    def __init__(self):
        self.global_tools: set[str] = set()
        self.group_tools: dict[str, set[str]] = {}
        self.channel_tools: dict[str, set[str]] = {}
        self.user_tools: dict[str, set[str]] = {}

    def can_use(self, user_id: str, channel: str, group: str, tool: str) -> bool:
        """Check permission hierarchy. Most specific wins."""
        # User-level override (most specific)
        if user_id in self.user_tools:
            return tool in self.user_tools[user_id]

        # Channel-level
        if channel in self.channel_tools:
            return tool in self.channel_tools[channel]

        # Group-level
        if group in self.group_tools:
            return tool in self.group_tools[group]

        # Global default
        return tool in self.global_tools
```

### Configuration Example

```yaml
# permissions.yaml
global:
  allowed_tools:
    - search_knowledge_base
    - get_weather
    - calculate

groups:
  admin:
    allowed_tools:
      - delete_file
      - modify_permissions
      - send_email
  support:
    allowed_tools:
      - search_knowledge_base
      - create_ticket
      - lookup_customer

channels:
  "#general":
    allowed_tools:
      - search_knowledge_base
  "#engineering":
    allowed_tools:
      - execute_code
      - search_codebase

users:
  "user_ceo":
    allowed_tools: ["*"]  # Full access (use sparingly)
```

---

## Sandbox Execution

### Types of Sandboxes

| Type | Isolation | Performance | Use Case |
|------|-----------|-------------|----------|
| **Host with gates** | Low | Fast | Trusted agents, simple tools |
| **Docker isolated** | High | Medium | Code execution, untrusted input |
| **Distributed nodes** | Maximum | Slow | Multi-tenant, production |

### Safe Command Execution

```python
import os
import subprocess
from pathlib import Path

BLOCKED_ENV_VARS = {
    "LD_PRELOAD", "LD_LIBRARY_PATH",
    "NODE_OPTIONS", "DYLD_INSERT_LIBRARIES",
    "PYTHONPATH", "PYTHONSTARTUP",
}

MAX_OUTPUT_SIZE = 200 * 1024  # 200KB
DEFAULT_TIMEOUT = 30  # seconds

class SecureExecutor:
    def __init__(self, allowed_dirs: list[str]):
        self.allowed_dirs = [Path(d).resolve() for d in allowed_dirs]

    def execute(self, command: str, working_dir: str) -> str:
        """Execute command with security checks."""
        # 1. Validate working directory
        resolved = Path(working_dir).resolve()
        if not any(resolved.is_relative_to(d) for d in self.allowed_dirs):
            raise SecurityError(f"Directory {working_dir} not in allowed paths")

        # 2. Strip dangerous env vars
        env = {k: v for k, v in os.environ.items() if k not in BLOCKED_ENV_VARS}

        # 3. Execute with timeout and output limits
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                timeout=DEFAULT_TIMEOUT,
                env=env,
                cwd=str(resolved),
                text=True,
            )
        except subprocess.TimeoutExpired:
            raise SecurityError(f"Command timed out after {DEFAULT_TIMEOUT}s")

        # 4. Truncate output to prevent context flooding
        output = result.stdout[:MAX_OUTPUT_SIZE]
        if len(result.stdout) > MAX_OUTPUT_SIZE:
            output += f"\n... [truncated, {len(result.stdout)} total bytes]"

        return output
```

### Path Traversal Protection

```python
def validate_path(user_path: str, base_dir: str) -> Path:
    """Prevent path traversal attacks."""
    base = Path(base_dir).resolve()
    requested = (base / user_path).resolve()

    if not requested.is_relative_to(base):
        raise SecurityError(
            f"Path traversal detected: {user_path} resolves outside {base_dir}"
        )

    return requested

# Usage
safe_path = validate_path("../../etc/passwd", "/app/data")
# Raises SecurityError
```

### Environment Variable Blocking

```python
DANGEROUS_ENV_VARS = {
    # Library injection
    "LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES",
    # Interpreter modification
    "NODE_OPTIONS", "PYTHONPATH", "PYTHONSTARTUP", "RUBYOPT",
    # Proxy hijacking
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    # Debug/profiling
    "NODE_DEBUG", "DEBUG",
}

def sanitize_environment(env: dict) -> dict:
    """Remove dangerous environment variables."""
    return {k: v for k, v in env.items() if k not in DANGEROUS_ENV_VARS}
```

### Output Truncation

```python
def truncate_output(output: str, max_bytes: int = 200 * 1024) -> str:
    """Truncate output to prevent context window flooding."""
    if len(output.encode()) <= max_bytes:
        return output

    # Truncate and add indicator
    truncated = output[:max_bytes]
    return truncated + f"\n\n[OUTPUT TRUNCATED: {len(output)} bytes total, showing first {max_bytes}]"
```

---

## Approval Workflows

### Operations Requiring Approval

```python
class ApprovalGate:
    """Gate for sensitive operations requiring human approval."""

    SENSITIVE_OPERATIONS = {
        "delete_file": "critical",
        "send_email": "high",
        "make_payment": "critical",
        "modify_permissions": "critical",
        "execute_sql_write": "high",
        "deploy_code": "high",
        "create_user": "medium",
    }

    def __init__(self, timeout_seconds: int = 300):
        self.timeout = timeout_seconds
        self.pending: dict[str, dict] = {}

    async def check(self, operation: str, details: dict, user_id: str) -> bool:
        """Check if operation needs approval and get it."""
        severity = self.SENSITIVE_OPERATIONS.get(operation)

        if severity is None:
            return True  # Auto-approve non-sensitive operations

        if severity == "critical":
            return await self._require_admin_approval(operation, details)
        elif severity == "high":
            return await self._require_user_confirmation(operation, details, user_id)
        else:
            return await self._require_user_acknowledgment(operation, details, user_id)

    async def _require_admin_approval(self, operation: str, details: dict) -> bool:
        """Critical operations need admin sign-off."""
        request_id = str(uuid.uuid4())
        self.pending[request_id] = {
            "operation": operation,
            "details": details,
            "created_at": datetime.utcnow(),
        }

        await notify_admins(f"Approval needed: {operation}\nDetails: {details}")

        # Wait for approval with timeout
        approved = await wait_for_approval(request_id, timeout=self.timeout)
        del self.pending[request_id]
        return approved
```

### Configurable Autonomy Levels

```python
from enum import Enum

class AutonomyLevel(Enum):
    AUTONOMOUS = "autonomous"          # Execute everything without asking
    SUPERVISED = "supervised"          # Ask for sensitive operations
    APPROVAL_REQUIRED = "approval"     # Ask for everything

class AgentConfig:
    autonomy: AutonomyLevel = AutonomyLevel.SUPERVISED

    def should_ask_approval(self, operation: str) -> bool:
        if self.autonomy == AutonomyLevel.AUTONOMOUS:
            return False
        if self.autonomy == AutonomyLevel.APPROVAL_REQUIRED:
            return True
        # SUPERVISED: only sensitive operations
        return operation in ApprovalGate.SENSITIVE_OPERATIONS
```

---

## Process Lifecycle Management

### Process Registry

```python
import asyncio
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ManagedProcess:
    pid: int
    command: str
    started_at: datetime
    timeout: int
    user_id: str
    status: str = "running"

class ProcessRegistry:
    """Track all processes started by agents."""

    def __init__(self):
        self.processes: dict[int, ManagedProcess] = {}
        self.audit_log: list[dict] = []

    def register(self, process: subprocess.Popen, command: str,
                 user_id: str, timeout: int = 30) -> ManagedProcess:
        managed = ManagedProcess(
            pid=process.pid,
            command=command,
            started_at=datetime.utcnow(),
            timeout=timeout,
            user_id=user_id,
        )
        self.processes[process.pid] = managed
        self._audit("start", managed)
        return managed

    def kill_if_expired(self):
        """Kill processes that exceeded their timeout."""
        now = datetime.utcnow()
        for pid, proc in list(self.processes.items()):
            elapsed = (now - proc.started_at).total_seconds()
            if elapsed > proc.timeout and proc.status == "running":
                try:
                    os.kill(pid, 9)
                    proc.status = "killed_timeout"
                    self._audit("kill_timeout", proc)
                except ProcessLookupError:
                    proc.status = "finished"

    def _audit(self, action: str, process: ManagedProcess):
        self.audit_log.append({
            "action": action,
            "pid": process.pid,
            "command": process.command,
            "user_id": process.user_id,
            "timestamp": datetime.utcnow().isoformat(),
        })
```

### Audit Logging

```python
class AuditLogger:
    """Log all agent actions for security review."""

    async def log_action(self, action: dict):
        """Log every action the agent takes."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": action["agent_id"],
            "user_id": action["user_id"],
            "tool": action["tool"],
            "input": action.get("input"),
            "output_summary": action.get("output", "")[:500],
            "approved": action.get("approved", True),
            "latency_ms": action.get("latency_ms"),
        }
        await self.store(entry)

        # Alert on suspicious patterns
        if await self._is_suspicious(entry):
            await alert_security_team(entry)

    async def _is_suspicious(self, entry: dict) -> bool:
        """Detect suspicious patterns."""
        # Too many actions in short time
        recent_count = await self.count_recent(
            agent_id=entry["agent_id"],
            window_seconds=60,
        )
        if recent_count > 50:
            return True

        # Sensitive tool used outside business hours
        hour = datetime.fromisoformat(entry["timestamp"]).hour
        if entry["tool"] in {"make_payment", "delete_file"} and (hour < 6 or hour > 22):
            return True

        return False
```

---

## DM/Channel Security

### Pairing Codes for Unknown Users

```python
import secrets

class UserVerification:
    """Verify unknown users before allowing agent access."""

    def __init__(self):
        self.verified_users: set[str] = set()
        self.pending_codes: dict[str, str] = {}  # user_id -> code

    def generate_pairing_code(self, user_id: str) -> str:
        """Generate a 6-digit code for verification."""
        code = secrets.token_hex(3).upper()  # e.g., "A1B2C3"
        self.pending_codes[user_id] = code
        return code

    def verify(self, user_id: str, code: str) -> bool:
        """Verify user with pairing code."""
        expected = self.pending_codes.get(user_id)
        if expected and expected == code:
            self.verified_users.add(user_id)
            del self.pending_codes[user_id]
            return True
        return False

    def is_verified(self, user_id: str) -> bool:
        return user_id in self.verified_users
```

### Rate Limiting

```python
from collections import defaultdict
import time

class RateLimiter:
    """Rate limit agent interactions per user."""

    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        now = time.time()
        # Clean old entries
        self.requests[user_id] = [
            t for t in self.requests[user_id]
            if now - t < self.window
        ]
        # Check limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False
        self.requests[user_id].append(now)
        return True
```

---

## Auth Profiles with Fallover

```python
@dataclass
class AuthProfile:
    name: str
    credentials: dict
    failure_count: int = 0
    max_failures: int = 3
    is_active: bool = True

class AuthManager:
    """Multiple credential sets with automatic fallback."""

    def __init__(self, profiles: list[AuthProfile]):
        self.profiles = profiles

    def get_active_profile(self) -> AuthProfile | None:
        """Get the first active profile with remaining retries."""
        for profile in self.profiles:
            if profile.is_active and profile.failure_count < profile.max_failures:
                return profile
        return None

    def report_failure(self, profile_name: str):
        """Record a failure and switch to backup if needed."""
        for profile in self.profiles:
            if profile.name == profile_name:
                profile.failure_count += 1
                if profile.failure_count >= profile.max_failures:
                    profile.is_active = False
                break

    def reset(self, profile_name: str):
        """Reset failure count after successful use."""
        for profile in self.profiles:
            if profile.name == profile_name:
                profile.failure_count = 0
                profile.is_active = True
                break
```

---

## Human-in-the-Loop by Design

### Visibility of All Actions

```python
class ActionLog:
    """Provide visibility into every agent action."""

    def format_for_user(self, actions: list[dict]) -> str:
        """Format action log for human review."""
        lines = []
        for action in actions:
            status = "approved" if action["approved"] else "BLOCKED"
            lines.append(
                f"[{action['timestamp']}] {action['tool']} — {status}"
            )
        return "\n".join(lines)
```

### Escalation to Human

```python
class EscalationHandler:
    """Escalate to human when agent is uncertain."""

    UNCERTAINTY_THRESHOLD = 0.6

    async def maybe_escalate(self, confidence: float, context: dict) -> bool:
        """Escalate if confidence is below threshold."""
        if confidence >= self.UNCERTAINTY_THRESHOLD:
            return False

        await notify_human(
            message=f"Agent needs help (confidence: {confidence:.0%})",
            context=context,
        )
        return True
```

---

## Context Window Security

### Prompt Injection Detection

```python
INJECTION_PATTERNS = [
    r"ignore (?:all )?(?:previous|above|prior) instructions",
    r"you are now",
    r"new instructions:",
    r"system:\s*you are",
    r"forget (?:everything|all|your)",
]

def detect_prompt_injection(text: str) -> bool:
    """Basic prompt injection detection."""
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
```

### Input Sanitization

```python
def sanitize_tool_output(output: str, max_size: int = 50000) -> str:
    """Sanitize tool output before adding to context."""
    # Truncate
    if len(output) > max_size:
        output = output[:max_size] + "\n[TRUNCATED]"

    # Remove potential injection attempts
    if detect_prompt_injection(output):
        return "[Tool output contained potential injection — sanitized]"

    return output
```

---

## Security Checklist

### Foundation
- [ ] Fail-closed: all tools blocked by default
- [ ] Tool allowlists configured per channel/user/group
- [ ] Rate limiting on all endpoints
- [ ] Audit logging for every agent action

### Execution
- [ ] Sandbox execution for code/commands
- [ ] Path traversal protection
- [ ] Dangerous env vars blocked
- [ ] Output truncation (200KB max)
- [ ] Process timeout enforcement

### Approval
- [ ] Sensitive operations require human approval
- [ ] Configurable autonomy levels
- [ ] Escalation paths for uncertain decisions
- [ ] Admin approval for critical operations

### Access
- [ ] User verification (pairing codes or allowlist)
- [ ] Auth profiles with fallover
- [ ] Credential rotation strategy
- [ ] No credentials in agent responses

### Context
- [ ] Prompt injection detection
- [ ] Tool output sanitization
- [ ] Context window size monitoring
- [ ] PII filtering in logs
