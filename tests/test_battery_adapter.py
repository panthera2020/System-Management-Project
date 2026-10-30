import pytest
from types import SimpleNamespace
from panther.services.battery_adapter import get_battery_status

def test_battery_present(monkeypatch):
    dummy = SimpleNamespace(percent=85, secsleft=5400, power_plugged=True)
    monkeypatch.setattr('panther.services.battery_adapter.psutil.sensors_battery', lambda: dummy)
    info = get_battery_status()
    assert info == {"percent": 85, "secsleft": 5400, "power_plugged": True}

def test_battery_absent(monkeypatch):
    monkeypatch.setattr('panther.services.battery_adapter.psutil.sensors_battery', lambda: None)
    info = get_battery_status()
    assert info == {}
