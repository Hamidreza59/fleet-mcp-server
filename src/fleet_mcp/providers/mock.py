"""In-memory provider backed by a bundled JSON file. No network, no secrets."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources

from fleet_mcp.models import (
    DTCDetail,
    FleetSummary,
    Measurement,
    TelematicsDevice,
    VehicleData,
)
from fleet_mcp.providers.base import VehicleNotFound


@lru_cache(maxsize=1)
def _load_raw() -> dict:
    with resources.files("fleet_mcp.data").joinpath("fleet.json").open("r", encoding="utf-8") as fh:
        return json.load(fh)


class MockTelematicsProvider:
    """Implements the `TelematicsProvider` protocol against synthetic data."""

    def __init__(self, raw: dict | None = None) -> None:
        self._raw = raw if raw is not None else _load_raw()

    # --- helpers -----------------------------------------------------------
    def _vehicle(self, vin: str, fleet_id: str) -> dict:
        v = self._raw["vehicles"].get(vin)
        if v is None or v["fleet_id"] != fleet_id:
            raise VehicleNotFound(f"No vehicle {vin} in fleet {fleet_id}")
        return v

    # --- protocol methods --------------------------------------------------
    def get_vehicle_data(self, vin: str, fleet_id: str) -> VehicleData:
        v = self._vehicle(vin, fleet_id)
        return VehicleData.model_validate(v)

    def get_telematics_device(self, unit_identifier: str, fleet_id: str) -> TelematicsDevice:
        d = self._raw["devices"].get(unit_identifier)
        if d is None:
            raise VehicleNotFound(f"No device {unit_identifier}")
        return TelematicsDevice.model_validate(d)

    def get_fleet_summary(self, fleet_id: str, timeframe: str) -> FleetSummary:
        fleet = self._raw["fleets"].get(fleet_id)
        if fleet is None:
            raise VehicleNotFound(f"No fleet {fleet_id}")
        tf = fleet["timeframes"].get(timeframe)
        if tf is None:
            raise ValueError(f"Unsupported timeframe '{timeframe}'. Use one of: 24h, 7d, 30d")

        members = [v for v in self._raw["vehicles"].values() if v["fleet_id"] == fleet_id]
        regions: dict[str, int] = {}
        for v in members:
            region = v["current_location"]["region"]
            regions[region] = regions.get(region, 0) + 1

        return FleetSummary(
            fleet_id=fleet_id,
            name=fleet["name"],
            timeframe=timeframe,
            total_vehicles=len(members),
            active_vehicles=tf["active_vehicles"],
            avg_fuel_efficiency_mpg=fleet["avg_fuel_efficiency_mpg"],
            total_mileage=tf["total_mileage"],
            maintenance_required=tf["maintenance_required"],
            regions=regions,
        )

    def get_vehicle_timeline(
        self, vin: str, fleet_id: str, start_date: str, end_date: str
    ) -> list[dict]:
        self._vehicle(vin, fleet_id)  # validates membership
        entries = self._raw.get("timelines", {}).get(vin, [])
        return [e for e in entries if start_date <= e["date"] <= end_date]

    def get_dtc_info(self, vin: str, fleet_id: str, dtc: str) -> DTCDetail:
        self._vehicle(vin, fleet_id)
        catalog = self._raw["dtc_catalog"].get(dtc.upper())
        if catalog is None:
            raise VehicleNotFound(f"Unknown DTC '{dtc}'")

        first = last = None
        for entry in self._raw.get("timelines", {}).get(vin, []):
            if dtc.upper() in entry["dtc_list"]:
                first = first or entry["date"]
                last = entry["date"]

        return DTCDetail(
            dtc=dtc.upper(),
            description=catalog["description"],
            category=catalog["category"],
            severity=catalog["severity"],
            earliest_appearance=first,
            last_seen=last,
        )

    def get_engine_measurements(
        self, vin: str, fleet_id: str, measurement: str, start_date: str, end_date: str
    ) -> list[Measurement]:
        self._vehicle(vin, fleet_id)
        series = self._raw.get("measurements", {}).get(vin, {}).get(measurement, [])
        out = [
            Measurement.model_validate(m)
            for m in series
            if start_date <= m["timestamp"][:10] <= end_date
        ]
        return out
