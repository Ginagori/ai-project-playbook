# AI Project Playbook MCP Server
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agent/ ./agent/
COPY mcp_server/ ./mcp_server/
COPY playbook/ ./playbook/
COPY scripts/ ./scripts/

# Create data directory for lessons database
RUN mkdir -p /app/data

# Set Python path
ENV PYTHONPATH=/app

# Default command - run MCP server
CMD ["python", "-m", "mcp_server.playbook_mcp"]
