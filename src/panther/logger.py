"""Structured logger for Panther.

Logs to console (INFO+) and to a rotating file (DEBUG+). Sensitive paths are redacted in the file output.
"""

import logging
import sys
from pathlib import Path
from .config import config

class SensitivePathFilter(logging.Filter):
    """Redact absolute paths that may contain user‑specific information.
    The filter replaces any occurrence of the project base directory with
    "[PROJECT_ROOT]" before the record is emitted.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "msg") and isinstance(record.msg, str):
            base = str(config.base_dir)
            record.msg = record.msg.replace(base, "[PROJECT_ROOT]")
        return True

def get_logger(name: str = "panther") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler (INFO+)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler (DEBUG+)
    log_file = Path(config.log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    fh.addFilter(SensitivePathFilter())
    logger.addHandler(fh)

    logger.debug("Logger initialized for %s", name)
    return logger
