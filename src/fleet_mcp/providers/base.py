"""Provider seam: swap the mock for a real telematics backend without touching tools."""

from __future__ import annotations

from typing import Protocol

from fleet_mcp.models import (
    DTCDetail,
    FleetSummary,
    Measurement,
    TelematicsDevice,
    VehicleData,
)


class VehicleNotFound(Exception):
    """Raised when a VIN / fleet combination is unknown to the provider."""


class TelematicsProvider(Protocol):
    """Everything the MCP tools need from a data source.

    A production implementation would issue authenticated GraphQL queries to a
    telematics platform. The mock implementation reads from a bundled JSON file.
    """

    def get_vehicle_data(self, vin: str, fleet_id: str) -> VehicleData: ...

    def get_telematics_device(self, unit_identifier: str, fleet_id: str) -> TelematicsDevice: ...

    def get_fleet_summary(self, fleet_id: str, timeframe: str) -> FleetSummary: ...

    def get_vehicle_timeline(
        self, vin: str, fleet_id: str, start_date: str, end_date: str
    ) -> list[dict]: ...

    def get_dtc_info(self, vin: str, fleet_id: str, dtc: str) -> DTCDetail: ...

    def get_engine_measurements(
        self, vin: str, fleet_id: str, measurement: str, start_date: str, end_date: str
    ) -> list[Measurement]: ...
