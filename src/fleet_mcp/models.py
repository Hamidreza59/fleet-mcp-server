"""Typed models for telematics payloads.

These mirror the shape of a real telematics GraphQL API response but contain
only synthetic data. Keeping them as Pydantic models gives the MCP tools clean,
self-documenting return schemas that agents can reason about.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Location(BaseModel):
    latitude: float
    longitude: float
    region: str
    timestamp: str


class VehicleIdentification(BaseModel):
    vin: str
    make: str
    model: str
    year: int
    trim: str | None = None
    vehicle_class: str = Field(alias="class", default="UNKNOWN")

    model_config = {"populate_by_name": True}


class DiagnosticStatus(BaseModel):
    is_mil_on: bool = Field(description="Is the malfunction indicator lamp (check-engine light) on?")
    timestamp: str


class OnBoardDiagnostics(BaseModel):
    dtc_list: list[str] = Field(default_factory=list)
    fuel_level: int | None = Field(default=None, description="Percent, 0-100")
    state_of_charge: int | None = Field(default=None, description="EV battery percent, 0-100")
    state_of_health: int | None = Field(default=None, description="EV battery health percent")
    status: DiagnosticStatus
    timestamp: str


class Battery(BaseModel):
    current_voltage: float
    timestamp: str


class VehicleData(BaseModel):
    traveled_distance: int
    current_location: Location
    identification: VehicleIdentification
    obd: OnBoardDiagnostics
    low_voltage_battery: Battery
    connectivity_source: str


class TelematicsDevice(BaseModel):
    vin: str
    unit_identifier: str
    device_type: str
    device_serial_number: str


class FleetSummary(BaseModel):
    fleet_id: str
    name: str
    timeframe: str
    total_vehicles: int
    active_vehicles: int
    avg_fuel_efficiency_mpg: float
    total_mileage: int
    maintenance_required: int
    regions: dict[str, int] = Field(description="region -> vehicle count")


class Measurement(BaseModel):
    name: str
    value: float
    unit: str
    timestamp: str


class DTCDetail(BaseModel):
    dtc: str
    description: str
    category: str
    severity: str
    earliest_appearance: str | None = None
    last_seen: str | None = None
