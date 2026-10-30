"""Configuration handling for Panther.

Loads defaults, can be overridden by environment variables.
"""

import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent  # project root
    src_dir: Path = base_dir / "src"
    data_dir: Path = base_dir / "data"
    db_path: Path = data_dir / "panther.db"
    log_path: Path = data_dir / "panther.log"

    # Application settings
    refresh_interval_seconds: int = int(os.getenv("PANTHER_REFRESH_INTERVAL", "5"))
    max_worker_threads: int = int(os.getenv("PANTHER_MAX_WORKERS", "4"))

    # UI defaults
    theme: str = os.getenv("PANTHER_THEME", "system")  # system / light / dark

    def __post_init__(self):
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

# Export a singleton for convenient import
config = Config()
