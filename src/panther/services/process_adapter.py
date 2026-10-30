"""Process service adapters.

Provides a thin wrapper around ``psutil`` to fetch the current process list.
If ``psutil`` is not available (e.g., during early CI steps), the functions raise
a clear ``RuntimeError`` so that callers can handle the situation gracefully.
"""

try:
    import psutil
except Exception:  # pragma: no cover – import may fail on fresh environments
    psutil = None

from typing import List, Dict, Any

def get_processes() -> List[Dict[str, Any]]:
    """Return a list of running processes with a minimal set of attributes.

    Each entry contains ``pid``, ``name``, ``cpu_percent`` and ``memory_info``
    (RSS in bytes). The function never blocks the UI thread – callers should
    invoke it from a background worker.
    """
    if psutil is None:
        raise RuntimeError("psutil is required for process enumeration")
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        info = p.info
        procs.append({
            "pid": info.get("pid"),
            "name": info.get("name"),
            "cpu_percent": info.get("cpu_percent"),
            "memory_rss": info.get("memory_info").rss if info.get("memory_info") else 0,
        })
    return procs
