"""Configuration handling for Panther.

Loads defaults, can be overridden by environment variables.
"""

import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    # Resolve per-user directory: %LOCALAPPDATA%\PantherSystemIntelligence
    _local_appdata = os.getenv("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    base_dir: Path = Path(_local_appdata) / "PantherSystemIntelligence"

    data_dir: Path = Path(os.getenv("PANTHER_DATA_DIR", str(base_dir / "data")))
    logs_dir: Path = base_dir / "logs"
    startup_log_path: Path = logs_dir / "startup.log"
    db_path: Path = Path(os.getenv("PANTHER_DB_PATH", str(data_dir / "panther.db")))
    log_path: Path = Path(os.getenv("PANTHER_LOG_PATH", str(data_dir / "panther.log")))

    # Application settings
    refresh_interval_seconds: int = int(os.getenv("PANTHER_REFRESH_INTERVAL", "5"))
    max_worker_threads: int = int(os.getenv("PANTHER_MAX_WORKERS", "4"))

    # UI defaults
    theme: str = os.getenv("PANTHER_THEME", "system")  # system / light / dark

    def __post_init__(self):
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

# Export a singleton for convenient import
config = Config()
