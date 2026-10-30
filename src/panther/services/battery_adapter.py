"""Battery service adapters.

Provides a simple wrapper around ``psutil.sensors_battery``. The function returns a
dictionary with the fields ``percent``, ``secsleft`` and ``power_plugged``. When no
battery is present an empty dict is returned, allowing the UI to handle the
"no battery" case gracefully.
"""

import psutil
from typing import Dict, Any

def get_battery_status() -> Dict[str, Any]:
    """Return battery information or an empty dict if unavailable.

    The dict mirrors the structure used by the UI screen:
    ``{"percent": int, "secsleft": int, "power_plugged": bool}``.
    """
    batt = psutil.sensors_battery()
    if batt is None:
        return {}
    return {
        "percent": batt.percent,
        "secsleft": batt.secsleft,
        "power_plugged": batt.power_plugged,
    }
