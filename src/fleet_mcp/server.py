"""Fleet telematics MCP server.

Exposes telematics tools and a RAG knowledge-search tool over the Model Context
Protocol. Run it over stdio (for desktop AI clients) or streamable HTTP (for
remote agents):

    fleet-mcp-server                      # stdio (default)
    FLEET_MCP_TRANSPORT=http fleet-mcp-server   # HTTP on :8080/mcp

Everything is backed by synthetic data — no credentials required.
"""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from fleet_mcp.providers import MockTelematicsProvider, TelematicsProvider
from fleet_mcp.providers.base import VehicleNotFound
from fleet_mcp.rag import build_knowledge_base

# --- wiring --------------------------------------------------------------
# Swap MockTelematicsProvider for a real GraphQL-backed provider here; the tools
# below are written against the TelematicsProvider protocol, not the mock.
provider: TelematicsProvider = MockTelematicsProvider()
knowledge_base = build_knowledge_base()

mcp = FastMCP(
    name="fleet-telematics",
    instructions=(
        "Tools for inspecting a vehicle fleet's telematics: per-vehicle data, "
        "fleet summaries, diagnostic trouble codes (DTCs), engine time series, "
        "and a maintenance knowledge base. Use search_maintenance_knowledge to "
        "explain DTCs or look up maintenance thresholds before giving advice."
    ),
)


# --- telematics tools ----------------------------------------------------
@mcp.tool()
def get_vehicle_data(vin: str, fleet_id: str) -> dict:
    """Get the latest telematics snapshot for one vehicle.

    Returns location, identification, on-board diagnostics (DTCs, fuel level or
    EV state of charge), and battery voltage.

    Args:
        vin: Vehicle Identification Number, e.g. "1HGCM82633A004352".
        fleet_id: Fleet the vehicle belongs to, e.g. "FLEET-ATLAS".
    """
    try:
        return provider.get_vehicle_data(vin, fleet_id).model_dump(by_alias=True)
    except VehicleNotFound as e:
        return {"error": str(e)}


@mcp.tool()
def get_telematics_device(unit_identifier: str, fleet_id: str) -> dict:
    """Look up the telematics device (modem/dongle) installed on a vehicle.

    Args:
        unit_identifier: Device unit id, e.g. "TD-000000".
        fleet_id: Fleet identifier.
    """
    try:
        return provider.get_telematics_device(unit_identifier, fleet_id).model_dump()
    except VehicleNotFound as e:
        return {"error": str(e)}


@mcp.tool()
def get_fleet_summary(fleet_id: str, timeframe: str = "24h") -> dict:
    """Get a fleet-wide rollup: vehicle counts, mileage, regions, maintenance due.

    Args:
        fleet_id: Fleet identifier, e.g. "FLEET-ATLAS".
        timeframe: One of "24h", "7d", "30d".
    """
    try:
        return provider.get_fleet_summary(fleet_id, timeframe).model_dump()
    except (VehicleNotFound, ValueError) as e:
        return {"error": str(e)}


@mcp.tool()
def get_vehicle_timeline(vin: str, fleet_id: str, start_date: str, end_date: str) -> list[dict]:
    """Get the daily DTC history for a vehicle over a date range.

    Args:
        vin: Vehicle Identification Number.
        fleet_id: Fleet identifier.
        start_date: Inclusive ISO date, e.g. "2026-06-07".
        end_date: Inclusive ISO date, e.g. "2026-06-09".
    """
    try:
        return provider.get_vehicle_timeline(vin, fleet_id, start_date, end_date)
    except VehicleNotFound as e:
        return [{"error": str(e)}]


@mcp.tool()
def get_dtc_info(vin: str, fleet_id: str, dtc: str) -> dict:
    """Get details for a diagnostic trouble code on a vehicle (description, severity, history).

    Args:
        vin: Vehicle Identification Number.
        fleet_id: Fleet identifier.
        dtc: The DTC to look up, e.g. "P0301".
    """
    try:
        return provider.get_dtc_info(vin, fleet_id, dtc).model_dump()
    except VehicleNotFound as e:
        return {"error": str(e)}


@mcp.tool()
def get_engine_measurements(
    vin: str, fleet_id: str, measurement: str, start_date: str, end_date: str
) -> list[dict]:
    """Get a time series of an engine measurement (e.g. "engine_rpm", "coolant_temp").

    Args:
        vin: Vehicle Identification Number.
        fleet_id: Fleet identifier.
        measurement: Measurement name, e.g. "coolant_temp".
        start_date: Inclusive ISO date.
        end_date: Inclusive ISO date.
    """
    try:
        series = provider.get_engine_measurements(vin, fleet_id, measurement, start_date, end_date)
        return [m.model_dump() for m in series]
    except VehicleNotFound as e:
        return [{"error": str(e)}]


# --- RAG tool ------------------------------------------------------------
@mcp.tool()
def search_maintenance_knowledge(query: str, top_k: int = 3) -> list[dict]:
    """Semantic search over the fleet maintenance knowledge base (RAG).

    Use this to explain what a DTC means, recommend a repair, or look up policy
    thresholds (fuel %, EV state of charge, battery health) before advising a
    fleet manager.

    Args:
        query: Natural-language question, e.g. "what does P0420 mean and is it urgent?".
        top_k: Number of knowledge chunks to return (default 3).
    """
    hits = knowledge_base.search(query, top_k=top_k)
    return [
        {"title": h.document.metadata.get("title"), "source": h.document.metadata.get("source"),
         "score": round(h.score, 4), "content": h.document.text}
        for h in hits
    ]


def main() -> None:
    transport = os.getenv("FLEET_MCP_TRANSPORT", "stdio").lower()
    if transport in ("http", "streamable-http"):
        # Served at http://<host>:<port>/mcp
        mcp.settings.host = os.getenv("FLEET_MCP_HOST", "0.0.0.0")
        mcp.settings.port = int(os.getenv("PORT", os.getenv("FLEET_MCP_PORT", "8080")))
        mcp.run(transport="streamable-http")
    elif transport == "sse":
        mcp.settings.host = os.getenv("FLEET_MCP_HOST", "0.0.0.0")
        mcp.settings.port = int(os.getenv("PORT", os.getenv("FLEET_MCP_PORT", "8080")))
        mcp.run(transport="sse")
    else:
        mcp.run()  # stdio


if __name__ == "__main__":
    main()
