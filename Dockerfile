# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLEET_MCP_TRANSPORT=http \
    PORT=8080

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip && pip install .

EXPOSE 8080
# Streamable-HTTP MCP endpoint is served at /mcp
CMD ["fleet-mcp-server"]
