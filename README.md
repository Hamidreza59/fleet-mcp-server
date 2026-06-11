# fleet-mcp-server

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that
exposes **fleet-telematics tools** and a **RAG knowledge-search tool** to any
MCP-compatible AI agent (Claude Desktop, a custom Bedrock agent, etc.).

> All data is **synthetic**. This is a sanitized, clean-room reference
> architecture for learning and portfolio use — no proprietary code or data.

It is the data/tool half of a two-part demo. The other half is
[`fleet-ai-agent`](https://github.com/Hamidreza59/fleet-ai-agent), a TypeScript
agent that connects to this server as an MCP client.

## What it exposes

| Tool | Purpose |
|------|---------|
| `get_vehicle_data` | Latest snapshot for one vehicle: location, DTCs, fuel/SoC, battery |
| `get_telematics_device` | The modem/dongle installed on a vehicle |
| `get_fleet_summary` | Fleet-wide rollup: counts, mileage, regions, maintenance due |
| `get_vehicle_timeline` | Daily DTC history over a date range |
| `get_dtc_info` | Description, severity, and history for a diagnostic trouble code |
| `get_engine_measurements` | Time series for a signal (e.g. `coolant_temp`) |
| `search_maintenance_knowledge` | **RAG**: semantic search over a maintenance knowledge base |

## Architecture

```
                 ┌─────────────────────────────────────────────┐
   MCP client →  │  FastMCP server (stdio | HTTP/SSE)           │
  (agent /       │                                             │
   Claude)       │   telematics tools ─► TelematicsProvider     │
                 │                        (Mock | GraphQL...)   │
                 │                                             │
                 │   search_maintenance_knowledge ─► RAG        │
                 │        Embedder → InMemoryVectorStore        │
                 └─────────────────────────────────────────────┘
```

Two seams make this production-shaped without production cost:

- **`TelematicsProvider`** — the tools call a protocol, not the mock. Swap
  `MockTelematicsProvider` for a real GraphQL/REST client (with IAM/OAuth2 auth)
  and the tools don't change. See `src/fleet_mcp/providers/`.
- **`Embedder`** — the vector store calls a protocol. The default
  `HashingEmbedder` is offline and free; swap in a Bedrock/Titan or OpenAI
  embedder for production-grade retrieval. See `src/fleet_mcp/rag/embedder.py`.

## Quick start

```bash
pip install -e ".[dev]"     # or: pip install .
pytest                      # run the tests

# stdio transport (for desktop AI clients)
fleet-mcp-server

# HTTP transport (for remote agents) → http://localhost:8080/mcp
FLEET_MCP_TRANSPORT=http fleet-mcp-server
```

### Use it from Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fleet-telematics": {
      "command": "fleet-mcp-server"
    }
  }
}
```

Then ask: *“Which vehicles in FLEET-ATLAS need maintenance, and why?”*

### Try the tools without an agent

```bash
# Inspector UI (requires Node):
npx @modelcontextprotocol/inspector fleet-mcp-server
```

## Docker

```bash
docker build -t fleet-mcp-server .
docker run -p 8080:8080 fleet-mcp-server   # serves /mcp over HTTP
```

## Project layout

```
src/fleet_mcp/
  server.py            # FastMCP app + tool definitions
  models.py            # Pydantic payload models
  providers/           # TelematicsProvider protocol + mock implementation
  rag/                 # Embedder, in-memory vector store, KB loader
  data/                # synthetic fleet.json + knowledge/*.md
tests/                 # pytest suite (tools + RAG)
```

## License

MIT — see [LICENSE](LICENSE).
