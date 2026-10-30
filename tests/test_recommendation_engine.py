import pytest
from panther.services.recommendation_engine import get_recommendations

def test_recommendations_thresholds():
    # High CPU and low battery should produce two recommendations
    metrics = {
        "cpu_percent": 85,
        "ram_percent": 50,
        "disk_percent": 30,
        "battery_percent": 15,
    }
    recs = get_recommendations(metrics)
    issues = {r["issue"] for r in recs}
    assert "High CPU usage" in issues
    assert "Low battery" in issues
    # No RAM or disk warnings
    assert all(r["issue"] != "High memory pressure" for r in recs)
    assert all(r["issue"] != "Low disk free space" for r in recs)

def test_no_recommendations_when_all_normal():
    metrics = {"cpu_percent": 10, "ram_percent": 30, "disk_percent": 40, "battery_percent": 80}
    recs = get_recommendations(metrics)
    assert recs == []
