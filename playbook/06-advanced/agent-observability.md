# Agent Observability Guide

A comprehensive guide for monitoring AI agents in production using Langfuse — traces, spans, scores, cost tracking, and dashboards.

## Quick Start

```bash
# 1. Install Langfuse SDK
pip install langfuse

# 2. Set environment variables
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_HOST=https://cloud.langfuse.com

# 3. Add tracing to your agent endpoint
# 4. Configure scores (rule-based + LLM judge + user feedback)
```

## Why Observability Matters for Agents

AI agents are fundamentally different from traditional software:

| Factor | Traditional Software | AI Agents |
|--------|---------------------|-----------|
| **Output** | Deterministic | Non-deterministic |
| **Cost** | Fixed per request | Variable (token-based) |
| **Quality** | Binary (works/broken) | Spectrum (excellent→terrible) |
| **Debugging** | Stack traces | Reasoning chains, tool calls |
| **Performance** | Latency only | Latency + token count + cost |

Without observability, you're flying blind: you don't know if your agent is providing good answers, how much it costs per user, or where quality is degrading.

---

## Langfuse Setup

### Cloud vs Self-Hosted

| Option | Pros | Cons |
|--------|------|------|
| **Cloud** (cloud.langfuse.com) | Zero setup, managed | Data leaves your infra |
| **Self-hosted** (Docker) | Full control, data stays local | Setup + maintenance |

### Cloud Setup

1. Sign up at [cloud.langfuse.com](https://cloud.langfuse.com)
2. Create a project
3. Copy your API keys from Settings → API Keys

### Environment Variables

```bash
# Required
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...

# Optional (defaults to cloud)
LANGFUSE_HOST=https://cloud.langfuse.com

# For self-hosted
LANGFUSE_HOST=http://localhost:3000
```

### Python SDK

```python
from langfuse import Langfuse

# Initialize (reads from env vars automatically)
langfuse = Langfuse()

# Or explicit configuration
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com",
)
```

---

## Core Concepts

### Hierarchy

```
Trace (end-to-end request)
├── Span: "retrieve-context"
│   ├── Span: "embed-query"
│   └── Span: "vector-search"
├── Generation: "main-llm-call" (LLM-specific)
│   └── model, tokens, cost
├── Span: "tool-execution"
│   ├── Span: "search-api"
│   └── Span: "format-results"
└── Score: "quality" = 0.85
```

### Traces

A trace represents one complete user interaction (e.g., one chat message → response cycle).

```python
trace = langfuse.trace(
    name="agent-response",
    user_id="user_123",
    session_id="conv_456",  # Groups traces in a conversation
    metadata={
        "agent_version": "1.2.0",
        "conversation_turn": 3,
    },
    tags=["production", "customer-support"],
)
```

### Spans

Spans track sub-operations within a trace. Use them for non-LLM operations.

```python
# Track retrieval
retrieval_span = trace.span(
    name="retrieve-context",
    input={"query": user_query, "top_k": 5},
)

results = await vector_db.search(user_query, limit=5)

retrieval_span.end(
    output={"num_results": len(results), "top_score": results[0].score},
)

# Track tool execution
tool_span = trace.span(
    name="tool-execution",
    input={"tool": "search_database", "params": {"table": "products"}},
)

tool_result = await execute_tool("search_database", params)

tool_span.end(
    output={"result_count": len(tool_result), "status": "success"},
)
```

### Generations

Generations are LLM-specific spans. They track model, tokens, and cost.

```python
generation = trace.generation(
    name="main-llm-call",
    model="claude-sonnet-4-5-20250929",
    model_parameters={"temperature": 0.7, "max_tokens": 1024},
    input=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ],
)

# Call the LLM
response = await anthropic.messages.create(
    model="claude-sonnet-4-5-20250929",
    messages=messages,
    max_tokens=1024,
)

generation.end(
    output=response.content[0].text,
    usage={
        "input": response.usage.input_tokens,
        "output": response.usage.output_tokens,
    },
)
```

### Scores

Scores attach quality metrics to traces. Three sources:

```python
# 1. Rule-based (every request, async)
trace.score(
    name="response-length",
    value=1.0 if len(response) > 50 else 0.0,
    comment=f"Length: {len(response)} chars",
)

trace.score(
    name="has-sources",
    value=1.0 if "[source]" in response else 0.0,
)

trace.score(
    name="latency",
    value=1.0 if latency < 3.0 else 0.5 if latency < 10.0 else 0.0,
    comment=f"{latency:.2f}s",
)

# 2. LLM Judge (sampled, 10%)
trace.score(
    name="judge-quality",
    value=judge_result["accuracy"] / 5.0,
    comment=judge_result["reasoning"],
)

# 3. User feedback (from frontend)
langfuse.score(
    trace_id=trace_id,
    name="user-feedback",
    value=1.0 if thumbs_up else 0.0,
    comment=user_comment,
)
```

---

## Full Instrumentation Example

```python
import time
import uuid
from langfuse import Langfuse

langfuse = Langfuse()

async def agent_endpoint(user_id: str, message: str, conversation_id: str):
    trace_id = str(uuid.uuid4())
    start_time = time.time()

    # Create trace
    trace = langfuse.trace(
        id=trace_id,
        name="agent-chat",
        user_id=user_id,
        session_id=conversation_id,
        input={"message": message},
    )

    # Step 1: Retrieve context
    retrieval = trace.span(name="retrieve-context", input={"query": message})
    context = await get_relevant_context(message)
    retrieval.end(output={"chunks": len(context)})

    # Step 2: Build prompt
    system_prompt = build_system_prompt(context)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    # Step 3: LLM call
    generation = trace.generation(
        name="main-response",
        model="claude-sonnet-4-5-20250929",
        input=messages,
    )

    response = await anthropic.messages.create(
        model="claude-sonnet-4-5-20250929",
        messages=messages,
        max_tokens=2048,
    )

    output_text = response.content[0].text
    generation.end(
        output=output_text,
        usage={
            "input": response.usage.input_tokens,
            "output": response.usage.output_tokens,
        },
    )

    # Step 4: Score
    latency = time.time() - start_time
    trace.score(name="latency", value=min(1.0, 5.0 / max(latency, 0.1)))
    trace.score(name="response-length", value=1.0 if 50 < len(output_text) < 5000 else 0.5)

    # Update trace with output
    trace.update(output={"response": output_text, "latency": latency})

    # IMPORTANT: Flush before returning
    langfuse.flush()

    return output_text
```

---

## Dashboard & Metrics

### Key Metrics to Track

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| **Latency (p50/p95/p99)** | Response speed | p95 > 10s |
| **Cost per conversation** | Budget impact | > $0.50/conversation |
| **Quality scores avg** | Overall quality | Avg < 0.7 |
| **Error rate** | System reliability | > 5% |
| **Token usage** | Efficiency | Sudden 2x increase |
| **User feedback ratio** | User satisfaction | Thumbs down > 30% |

### Langfuse Dashboard Features

- **Trace Explorer**: Browse individual traces, see full LLM inputs/outputs
- **Score Analytics**: Quality scores over time, distributions
- **Model Comparison**: Compare performance across model versions
- **Cost Tracking**: Cost per model, per user, per feature
- **Session View**: See full conversation flows across multiple turns

### Setting Up Alerts

```python
# Example: Daily quality check
async def daily_quality_check():
    """Run daily and alert if quality drops."""
    scores = await langfuse.get_scores(
        name="judge-quality",
        from_timestamp=yesterday(),
    )

    avg_quality = sum(s.value for s in scores) / len(scores)

    if avg_quality < 0.7:
        await send_alert(
            channel="slack",
            message=f"Quality alert: Average score dropped to {avg_quality:.2f}",
        )
```

---

## Multi-Agent Observability

When multiple agents collaborate, use parent-child traces:

```python
# Parent agent creates trace
parent_trace = langfuse.trace(
    name="orchestrator",
    metadata={"pattern": "supervisor"},
)

# Child agent 1
child1_span = parent_trace.span(
    name="researcher-agent",
    input={"task": "Find relevant documentation"},
)
result1 = await researcher.run(task)
child1_span.end(output=result1)

# Child agent 2 (uses result from child 1)
child2_span = parent_trace.span(
    name="writer-agent",
    input={"task": "Write summary", "research": result1},
)
result2 = await writer.run(task, context=result1)
child2_span.end(output=result2)
```

---

## Cost Tracking

### Per-Model Cost Configuration

Langfuse auto-calculates costs for known models. For custom pricing:

```python
# Custom cost tracking
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = {
        "claude-opus-4-6": {"input": 15.0, "output": 75.0},
        "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
        "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
    }
    rates = pricing.get(model, {"input": 3.0, "output": 15.0})
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000
```

### Cost by User/Feature

```sql
-- Cost per user (Langfuse SQL)
SELECT
    user_id,
    SUM(calculated_total_cost) as total_cost,
    COUNT(*) as num_traces,
    AVG(calculated_total_cost) as avg_cost_per_trace
FROM traces
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY user_id
ORDER BY total_cost DESC;
```

---

## OpenTelemetry Integration

Langfuse handles AI-specific observability. For infrastructure monitoring, use OpenTelemetry alongside it:

| Concern | Tool |
|---------|------|
| LLM calls, quality scores | Langfuse |
| HTTP latency, error rates | OpenTelemetry |
| Database queries | OpenTelemetry |
| Infrastructure metrics | Prometheus/Grafana |

```python
# Both can coexist
from langfuse import Langfuse
from opentelemetry import trace as otel_trace

langfuse = Langfuse()
tracer = otel_trace.get_tracer("my-agent")

@tracer.start_as_current_span("agent-endpoint")
async def agent_endpoint(request):
    # OTEL tracks HTTP-level metrics
    # Langfuse tracks AI-specific metrics
    lf_trace = langfuse.trace(name="agent-response")
    ...
```

---

## Best Practices

1. **Always flush before process exit**: `langfuse.flush()` — SDK buffers events
2. **Use structured metadata**: Enables filtering in dashboard
3. **Sample expensive evaluations**: LLM Judge at 10%, not 100%
4. **Set retention policies**: Don't keep traces forever (90 days default)
5. **Don't log PII in traces**: Mask sensitive data before logging
6. **Use session IDs**: Group conversation turns together
7. **Tag traces**: Use tags for environment, agent version, feature flags
8. **Monitor cost trends**: Set up alerts for cost spikes
9. **Version your prompts**: Track which prompt version produced which quality
10. **Export data regularly**: Back up scores and traces for offline analysis

---

## Observability Checklist

### Setup
- [ ] Langfuse SDK installed and configured
- [ ] Environment variables set (public key, secret key, host)
- [ ] Trace creation on every agent request

### Instrumentation
- [ ] Spans for retrieval, tool execution, reasoning steps
- [ ] Generations for all LLM calls (with token usage)
- [ ] Session IDs for conversation grouping
- [ ] User IDs for per-user tracking

### Scoring
- [ ] Rule-based scores on every request (async)
- [ ] LLM Judge on 10% sample
- [ ] User feedback collection (thumbs up/down)

### Monitoring
- [ ] Daily quality score check
- [ ] Cost alerts configured
- [ ] Latency monitoring (p95 threshold)
- [ ] Error rate tracking
