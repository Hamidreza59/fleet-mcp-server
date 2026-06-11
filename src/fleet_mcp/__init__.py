"""Fleet telematics MCP server.

Exposes a small, well-typed set of telematics tools (vehicle data, fleet
summaries, diagnostic trouble codes, engine measurements) plus a RAG-backed
maintenance-knowledge search tool to any MCP-compatible AI agent.

All data is synthetic. This is a sanitized, clean-room reference architecture
intended for learning and portfolio use.
"""

__version__ = "0.1.0"
