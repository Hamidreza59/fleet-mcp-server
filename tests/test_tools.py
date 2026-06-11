"""Tests for the provider-backed telematics tools."""

import pytest

from fleet_mcp.providers import MockTelematicsProvider
from fleet_mcp.providers.base import VehicleNotFound

ATLAS = "FLEET-ATLAS"
TRANSIT = "1FTBW2CMXKKB10001"


@pytest.fixture
def provider() -> MockTelematicsProvider:
    return MockTelematicsProvider()


def test_get_vehicle_data_returns_dtcs_and_fuel(provider):
    data = provider.get_vehicle_data(TRANSIT, ATLAS)
    assert data.identification.make == "Ford"
    assert "P0301" in data.obd.dtc_list
    assert data.obd.fuel_level == 18


def test_get_vehicle_data_wrong_fleet_raises(provider):
    with pytest.raises(VehicleNotFound):
        provider.get_vehicle_data(TRANSIT, "FLEET-NORTHWIND")


def test_fleet_summary_counts_members_and_regions(provider):
    summary = provider.get_fleet_summary(ATLAS, "24h")
    assert summary.total_vehicles == 4
    assert sum(summary.regions.values()) == 4
    assert summary.maintenance_required == 2


def test_fleet_summary_rejects_bad_timeframe(provider):
    with pytest.raises(ValueError):
        provider.get_fleet_summary(ATLAS, "1y")


def test_dtc_info_includes_severity_and_history(provider):
    dtc = provider.get_dtc_info(TRANSIT, ATLAS, "p0301")  # case-insensitive
    assert dtc.dtc == "P0301"
    assert dtc.severity == "HIGH"
    assert dtc.last_seen == "2026-06-09"


def test_timeline_filters_by_date(provider):
    entries = provider.get_vehicle_timeline(TRANSIT, ATLAS, "2026-06-08", "2026-06-09")
    assert len(entries) == 2
    assert entries[0]["date"] == "2026-06-08"


def test_engine_measurements_time_series(provider):
    series = provider.get_engine_measurements(
        TRANSIT, ATLAS, "coolant_temp", "2026-06-09", "2026-06-09"
    )
    assert len(series) == 3
    assert series[-1].value == pytest.approx(101.2)
