"""System monitoring service adapters.

Provides lightweight functions that wrap psutil (and, where needed, native Windows APIs) to fetch
CPU, RAM, disk and battery information. All calls are pure functions – they contain no
Qt or UI logic, satisfying the rule that business logic stays independent of the UI.
"""

import psutil
from typing import Dict, Any

def get_cpu_percent() -> float:
    """Return the overall CPU utilisation as a percentage (0‑100)."""
    return psutil.cpu_percent(interval=0.1)

def get_ram_usage() -> Dict[str, Any]:
    """Return a mapping with total, available and used RAM (bytes) and usage percent."""
    vm = psutil.virtual_memory()
    return {
        "total": vm.total,
        "available": vm.available,
        "used": vm.used,
        "percent": vm.percent,
    }

def get_disk_usage(path: str = "C:\\") -> Dict[str, Any]:
    """Return disk usage statistics for *path* (default=C:\\ on Windows)."""
    du = psutil.disk_usage(path)
    return {
        "total": du.total,
        "used": du.used,
        "free": du.free,
        "percent": du.percent,
    }

def get_battery_info() -> Dict[str, Any]:
    """Return battery status if present, otherwise an empty dict.

    The dict contains *percent*, *secsleft*, *power_plugged* and *status* (a short
    human‑readable string). When psutil cannot find a battery, the dict is empty.
    """
    batt = psutil.sensors_battery()
    if batt is None:
        return {}
    return {
        "percent": batt.percent,
        "secsleft": batt.secsleft,
        "power_plugged": batt.power_plugged,
    }
