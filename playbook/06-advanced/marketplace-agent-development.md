# Marketplace & Agent Development Guide

A comprehensive guide for developing, publishing, and managing AI agents in a marketplace — digital employees, plugin architecture, multi-channel delivery, and quality gates.

## What Is an Agent Marketplace?

An agent marketplace is a platform where:
- **Creators** build and publish AI agents (digital employees)
- **Users** discover, install, and use agents for their business
- **Platform** handles billing, discovery, ratings, and infrastructure

Think of it as an "App Store for AI agents" — each agent specializes in a role (customer support, data analysis, project management) and users pick the ones they need.

---

## Anatomy of a Digital Employee

```python
from dataclasses import dataclass, field
from enum import Enum

class AgentStatus(Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"

@dataclass
class DigitalEmployee:
    # Identity
    name: str                          # "Customer Support Agent"
    role: str                          # "customer_support"
    description: str                   # What this agent does
    author: str                        # Creator's name/org
    version: str                       # "1.2.0"

    # Capabilities
    capabilities: list[str]            # ["query_database", "send_email"]
    tools: list[str]                   # MCP tools it can use
    required_context: list[str]        # ["knowledge_base", "customer_data"]

    # Configuration
    config_schema: dict                # JSON Schema for customizable settings
    default_config: dict               # Default settings

    # Marketplace
    pricing: dict                      # {"model": "per_use", "price": 0.01}
    status: AgentStatus = AgentStatus.DRAFT
    rating: float = 0.0                # 0.0-5.0
    installs: int = 0
    tags: list[str] = field(default_factory=list)

    # Quality
    eval_pass_rate: float = 0.0        # Golden dataset pass rate
    avg_latency_ms: float = 0.0        # P50 latency
    error_rate: float = 0.0            # % of failed interactions
```

---

## Development Lifecycle

```
Design → Implement → Test → Review → Publish → Monitor
  │         │          │       │         │         │
  │    Build agent   Quality  Code +   Submit    Track
  │    logic, tools  gates    behavior  with      usage,
  │    prompts       (evals)  review    metadata  ratings
  │
  Define role,
  capabilities,
  user stories
```

### Phase 1: Design

```markdown
# Agent Design Document

## Role
Customer Support Agent for SaaS products

## User Stories
- As a customer, I can ask questions about billing and get accurate answers
- As a customer, I can request a refund and the agent processes it
- As a support manager, I can see agent performance metrics

## Capabilities
1. Search knowledge base for answers
2. Look up customer account details
3. Process refunds (with approval for >$100)
4. Create support tickets
5. Escalate to human for complex issues

## Access Requirements
- Read: knowledge_base, customer_accounts
- Write: support_tickets
- Execute: process_refund (with approval gate)

## Success Criteria
- 80% of questions answered without human escalation
- Average response time < 3 seconds
- Customer satisfaction > 4.0/5.0
```

### Phase 2: Implement

```python
class CustomerSupportAgent:
    def __init__(self, config: dict):
        self.tone = config.get("tone", "friendly")
        self.autonomy = config.get("autonomy", "supervised")
        self.max_refund = config.get("max_refund_without_approval", 100)

    async def handle_message(self, message: str, context: dict) -> str:
        # 1. Classify intent
        intent = await self.classify(message)

        # 2. Route to handler
        match intent:
            case "question":
                return await self.answer_question(message, context)
            case "refund":
                return await self.process_refund(message, context)
            case "complaint":
                return await self.handle_complaint(message, context)
            case _:
                return await self.general_response(message, context)

    async def answer_question(self, message: str, context: dict) -> str:
        # Search knowledge base
        results = await self.tools.search_knowledge_base(message)
        if not results:
            return await self.escalate_to_human(message, "No KB results")

        # Generate response
        return await self.generate(
            system=f"You are a {self.tone} customer support agent. "
                   f"Answer using ONLY the provided context.",
            context=results,
            question=message,
        )
```

### Phase 3: Test (Quality Gates)

```python
class QualityGate:
    """Quality gates that must pass before marketplace publication."""

    CHECKS = [
        ("eval_pass_rate", 0.8, "Golden dataset pass rate >= 80%"),
        ("security_audit", True, "Security audit passed"),
        ("p95_latency_ms", 5000, "P95 latency under 5 seconds"),
        ("has_readme", True, "README.md exists"),
        ("has_examples", 3, "At least 3 usage examples"),
        ("no_pii_leaks", True, "No PII in responses (tested)"),
        ("error_rate", 0.05, "Error rate under 5%"),
    ]

    def evaluate(self, metrics: dict) -> tuple[bool, list[str]]:
        """Run all quality gates. Returns (passed, failures)."""
        failures = []

        for name, threshold, message in self.CHECKS:
            value = metrics.get(name)
            if value is None:
                failures.append(f"MISSING: {message} (metric not provided)")
                continue

            if isinstance(threshold, bool):
                if value != threshold:
                    failures.append(f"FAILED: {message}")
            elif isinstance(threshold, float) and threshold < 1:
                # For rates: value should be >= threshold
                if value < threshold:
                    failures.append(f"FAILED: {message} (got {value:.1%})")
            else:
                # For counts/latency: value should be <= threshold
                if value > threshold:
                    failures.append(f"FAILED: {message} (got {value})")

        return len(failures) == 0, failures
```

---

## Agent Configuration

Agents should be customizable by users without code changes.

### Configuration Schema

```python
# JSON Schema for agent configuration
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "tone": {
            "type": "string",
            "enum": ["formal", "casual", "friendly", "professional"],
            "default": "friendly",
            "description": "Communication style",
        },
        "autonomy": {
            "type": "string",
            "enum": ["autonomous", "supervised", "approval_required"],
            "default": "supervised",
            "description": "How much the agent can do without asking",
        },
        "max_actions_per_hour": {
            "type": "integer",
            "minimum": 1,
            "maximum": 100,
            "default": 20,
            "description": "Rate limit on agent actions",
        },
        "working_hours": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": False},
                "start": {"type": "string", "format": "time", "default": "09:00"},
                "end": {"type": "string", "format": "time", "default": "17:00"},
                "timezone": {"type": "string", "default": "UTC"},
            },
        },
        "notification_channels": {
            "type": "array",
            "items": {"type": "string", "enum": ["web", "email", "slack"]},
            "default": ["web"],
        },
    },
}
```

### Configuration Validation

```python
from pydantic import BaseModel, validator
from typing import Optional

class AgentConfig(BaseModel):
    tone: str = "friendly"
    autonomy: str = "supervised"
    max_actions_per_hour: int = 20
    working_hours: Optional[dict] = None
    notification_channels: list[str] = ["web"]

    @validator("tone")
    def valid_tone(cls, v):
        allowed = {"formal", "casual", "friendly", "professional"}
        if v not in allowed:
            raise ValueError(f"Tone must be one of {allowed}")
        return v

    @validator("autonomy")
    def valid_autonomy(cls, v):
        allowed = {"autonomous", "supervised", "approval_required"}
        if v not in allowed:
            raise ValueError(f"Autonomy must be one of {allowed}")
        return v
```

---

## Interaction Patterns

### Delegation

Human assigns task, agent executes.

```python
async def handle_delegation(agent, task: str, user_id: str):
    """Human delegates a task to the agent."""
    # Acknowledge
    await notify(user_id, f"Got it. Working on: {task}")

    # Execute
    result = await agent.execute(task)

    # Report back
    await notify(user_id, f"Done: {result.summary}")
    return result
```

### Reporting

Agent sends updates at configured intervals.

```python
async def send_status_report(agent, user_id: str):
    """Agent proactively sends status report."""
    report = await agent.generate_report()
    await notify(user_id, f"Status Update:\n{report}")
```

### Escalation

Agent recognizes it can't handle something and escalates.

```python
async def maybe_escalate(agent, message: str, confidence: float) -> bool:
    """Escalate to human if confidence is low."""
    if confidence < 0.6:
        await notify_human(
            f"Agent needs help:\n"
            f"User message: {message}\n"
            f"Confidence: {confidence:.0%}\n"
            f"Please respond directly."
        )
        return True
    return False
```

---

## Multi-Agent Communication

Inspired by OpenClaw's "virtual meeting room" pattern — agents can communicate with each other.

### Agent-to-Agent Messaging

```python
class AgentCommunication:
    """Enable agents to communicate within a session."""

    def __init__(self, session_manager):
        self.sessions = session_manager

    async def send_to_agent(self, from_agent: str, to_agent: str,
                             message: str, context: dict = None) -> str:
        """Send a message from one agent to another."""
        session = await self.sessions.get_or_create(to_agent)

        response = await session.send({
            "from": from_agent,
            "message": message,
            "context": context or {},
            "reply_to": from_agent,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return response

    async def spawn_agent(self, agent_type: str, task: str,
                          parent_session: str) -> str:
        """Spawn a new agent session for a subtask."""
        session_id = await self.sessions.create(
            agent_type=agent_type,
            initial_message=task,
            metadata={"parent_session": parent_session},
        )
        return session_id

    async def broadcast(self, from_agent: str, message: str,
                        agents: list[str]):
        """Send a message to multiple agents."""
        tasks = [
            self.send_to_agent(from_agent, agent, message)
            for agent in agents
        ]
        return await asyncio.gather(*tasks)
```

### Meeting Room Pattern

```python
class VirtualMeetingRoom:
    """Agents collaborate in a shared session."""

    def __init__(self, participants: list[str]):
        self.participants = participants
        self.transcript: list[dict] = []

    async def discuss(self, topic: str, max_rounds: int = 5) -> str:
        """Agents discuss a topic and reach consensus."""
        self.transcript.append({"role": "system", "content": f"Topic: {topic}"})

        for round_num in range(max_rounds):
            for agent_name in self.participants:
                agent = get_agent(agent_name)
                response = await agent.respond(
                    context=self.transcript,
                    instruction=f"Contribute your perspective on: {topic}",
                )
                self.transcript.append({
                    "role": agent_name,
                    "content": response,
                    "round": round_num,
                })

            # Check for consensus
            if await self._check_consensus():
                break

        return await self._summarize_discussion()
```

---

## Plugin Architecture

Inspired by OpenClaw — allow third-party developers to extend agents with plugins.

### Plugin SDK

```python
from abc import ABC, abstractmethod

class Plugin(ABC):
    """Base class for agent plugins."""

    @abstractmethod
    def get_name(self) -> str:
        """Unique plugin name."""
        ...

    @abstractmethod
    def get_version(self) -> str:
        """Plugin version (semver)."""
        ...

    def get_tools(self) -> list[dict]:
        """Return tools this plugin provides."""
        return []

    def get_routes(self) -> list[dict]:
        """Return HTTP routes this plugin provides."""
        return []

    def on_install(self, config: dict):
        """Called when plugin is installed."""
        pass

    def on_uninstall(self):
        """Called when plugin is removed."""
        pass

    def on_message(self, message: dict) -> dict | None:
        """Hook into message processing. Return modified message or None."""
        return None
```

### Plugin Manager

```python
class PluginManager:
    """Dynamic plugin loading and management."""

    def __init__(self):
        self.plugins: dict[str, Plugin] = {}
        self.tools: dict[str, callable] = {}
        self.routes: list[dict] = []

    def register(self, plugin: Plugin, config: dict = None):
        """Register a plugin and its tools/routes."""
        name = plugin.get_name()
        self.plugins[name] = plugin

        # Register tools
        for tool in plugin.get_tools():
            tool_name = f"{name}_{tool['name']}"
            self.tools[tool_name] = tool["handler"]

        # Register routes
        for route in plugin.get_routes():
            route["plugin"] = name
            self.routes.append(route)

        # Notify plugin
        plugin.on_install(config or {})

    def unregister(self, name: str):
        """Remove a plugin."""
        if name in self.plugins:
            self.plugins[name].on_uninstall()
            # Remove tools
            self.tools = {k: v for k, v in self.tools.items()
                         if not k.startswith(f"{name}_")}
            # Remove routes
            self.routes = [r for r in self.routes if r.get("plugin") != name]
            del self.plugins[name]
```

### Example Plugin

```python
class WeatherPlugin(Plugin):
    def get_name(self) -> str:
        return "weather"

    def get_version(self) -> str:
        return "1.0.0"

    def get_tools(self) -> list[dict]:
        return [{
            "name": "get_forecast",
            "description": "Get weather forecast for a location",
            "handler": self.get_forecast,
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "days": {"type": "integer", "default": 3},
                },
                "required": ["location"],
            },
        }]

    async def get_forecast(self, location: str, days: int = 3) -> dict:
        # Call weather API
        response = await httpx.get(f"https://api.weather.com/forecast", params={
            "location": location, "days": days,
        })
        return response.json()
```

---

## Multi-Channel Delivery

Agents can deliver messages through multiple channels, each with different formatting requirements.

### Unified Message Envelope

```python
@dataclass
class Attachment:
    type: str  # "image", "file", "audio"
    url: str
    name: str
    size_bytes: int = 0

@dataclass
class Action:
    type: str  # "button", "quick_reply"
    label: str
    value: str

@dataclass
class MessageEnvelope:
    """Channel-agnostic message format."""
    content: str
    attachments: list[Attachment] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    channel_overrides: dict = field(default_factory=dict)
```

### Channel Adapters

```python
class ChannelAdapter:
    """Base class for channel-specific delivery."""

    @abstractmethod
    def get_max_length(self) -> int:
        ...

    @abstractmethod
    def format_message(self, envelope: MessageEnvelope) -> dict:
        ...

    def chunk_message(self, content: str) -> list[str]:
        """Split long messages for channels with size limits."""
        max_len = self.get_max_length()
        if len(content) <= max_len:
            return [content]
        # Split at paragraph boundaries
        chunks = []
        current = ""
        for paragraph in content.split("\n\n"):
            if len(current) + len(paragraph) + 2 > max_len:
                chunks.append(current.strip())
                current = paragraph
            else:
                current += "\n\n" + paragraph
        if current.strip():
            chunks.append(current.strip())
        return chunks

class WhatsAppAdapter(ChannelAdapter):
    def get_max_length(self) -> int:
        return 4096

    def format_message(self, envelope: MessageEnvelope) -> dict:
        return {
            "messaging_product": "whatsapp",
            "type": "text",
            "text": {"body": envelope.content[:4096]},
        }

class SlackAdapter(ChannelAdapter):
    def get_max_length(self) -> int:
        return 40000

    def format_message(self, envelope: MessageEnvelope) -> dict:
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": envelope.content}}]
        if envelope.actions:
            blocks.append({
                "type": "actions",
                "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": a.label},
                     "value": a.value}
                    for a in envelope.actions
                ],
            })
        return {"blocks": blocks}

class WebAdapter(ChannelAdapter):
    def get_max_length(self) -> int:
        return 100000  # Practically unlimited

    def format_message(self, envelope: MessageEnvelope) -> dict:
        return {
            "content": envelope.content,
            "attachments": [a.__dict__ for a in envelope.attachments],
            "actions": [a.__dict__ for a in envelope.actions],
        }
```

### Channel Support Matrix

| Channel | Max Length | Rich Text | Buttons | Files | Real-time |
|---------|-----------|-----------|---------|-------|-----------|
| Web | Unlimited | Full HTML/MD | Yes | Yes | WebSocket |
| WhatsApp | 4,096 | Limited | Quick replies | Yes | Webhook |
| Telegram | 4,096 | Markdown | Inline keyboard | Yes | Webhook |
| Discord | 2,000 | Markdown | Buttons | Yes | WebSocket |
| Slack | 40,000 | Blocks (mrkdwn) | Blocks | Yes | WebSocket |
| Email | Unlimited | Full HTML | Links | Attachments | Async |
| SMS | 160 | None | None | No | Async |

### Delivery Tracking

```python
@dataclass
class DeliveryAttempt:
    channel: str
    status: str  # "sent", "delivered", "read", "failed"
    timestamp: datetime
    error: str | None = None

class DeliveryTracker:
    async def track(self, message_id: str, channel: str, status: str,
                    error: str = None):
        await db.insert("delivery_attempts", {
            "message_id": message_id,
            "channel": channel,
            "status": status,
            "error": error,
            "timestamp": datetime.utcnow(),
        })
```

---

## Marketplace Economics

### Pricing Your Agent

| Model | When to Use | Example |
|-------|-------------|---------|
| **Free** | Attract users, basic features | Free tier with 100 uses/month |
| **Per-use** | Usage-based value | $0.01 per interaction |
| **Monthly** | Predictable revenue | $29/month per agent |
| **Freemium** | Growth then monetize | Free basic, $49 for premium |

### Rating System

```python
@dataclass
class AgentReview:
    user_id: str
    agent_id: str
    rating: int  # 1-5 stars
    title: str
    body: str
    helpful_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

# Aggregate rating with recency weighting
async def calculate_rating(agent_id: str) -> float:
    reviews = await db.query(
        "SELECT rating, created_at FROM agent_reviews WHERE agent_id = $1",
        agent_id,
    )
    if not reviews:
        return 0.0

    # Recent reviews weighted more
    total_weight = 0
    weighted_sum = 0
    now = datetime.utcnow()
    for review in reviews:
        days_old = (now - review["created_at"]).days
        weight = max(0.1, 1.0 - (days_old / 365))  # Decay over a year
        weighted_sum += review["rating"] * weight
        total_weight += weight

    return round(weighted_sum / total_weight, 1)
```

### Revenue Split

```
User pays $29/month for an agent:
├── Platform fee (20%): $5.80
├── Payment processing (3%): $0.87
└── Creator receives (77%): $22.33
```

### Creator Dashboard Metrics

| Metric | Description |
|--------|-------------|
| Installs | Total users using the agent |
| Active users | Users who interacted this month |
| Revenue | Monthly revenue from the agent |
| Rating | Current average rating |
| Satisfaction | % of positive feedback |
| Error rate | % of failed interactions |
| Avg latency | P50 response time |

---

## Publishing Checklist

### Before Submission
- [ ] Agent design document complete
- [ ] Core functionality implemented and working
- [ ] Configuration schema defined with defaults
- [ ] Golden dataset with 20+ test cases
- [ ] Eval pass rate >= 80%
- [ ] Security audit passed (no PII leaks, no prompt injection)
- [ ] P95 latency under 5 seconds
- [ ] Error rate under 5%

### Documentation
- [ ] README with description and use cases
- [ ] At least 3 usage examples
- [ ] Configuration guide
- [ ] Known limitations documented

### Marketplace Metadata
- [ ] Clear, descriptive name
- [ ] Role and capabilities listed
- [ ] Tags for discovery
- [ ] Pricing model configured
- [ ] Screenshots or demo video
- [ ] Version number set

### Post-Publication
- [ ] Monitor ratings and reviews
- [ ] Track error rates in production
- [ ] Respond to user feedback
- [ ] Regular updates and improvements
- [ ] Version changelog maintained
