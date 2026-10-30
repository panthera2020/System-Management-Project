"""Application entry point for Panther.

Running this module starts the Qt event loop and shows the main window.
All heavy work is delegated to background workers.
"""

import sys
import os
import traceback
from datetime import datetime
from PySide6.QtWidgets import QApplication

from .config import config
from .logger import get_logger


def log_startup(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"[{timestamp}] [STARTUP] {message}"
    print(line, flush=True)
    try:
        config.startup_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config.startup_log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Warning: Failed writing to startup log: {e}", file=sys.stderr)


def main() -> int:
    try:
        log_startup("=== Panther System Intelligence Startup Begin ===")
        log_startup(f"Python: {sys.version}")
        log_startup(f"Executable: {sys.executable}")
        log_startup(f"Working Directory: {os.getcwd()}")
        log_startup(f"Data directory: {config.data_dir}")
        log_startup(f"DB path: {config.db_path}")
        log_startup(f"Startup log path: {config.startup_log_path}")

        # Initialize application logger
        logger = get_logger("panther.main")
        logger.info("Starting Panther System Intelligence UI")

        # Step 1: Ensure database is initialized
        log_startup("Initializing / verifying database connection...")
        from .db import db
        log_startup("Database initialized successfully.")

        # Step 2: Initialize QApplication
        log_startup("Initializing QApplication...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
            log_startup("QApplication instance created.")
        else:
            log_startup("Using existing QApplication instance.")

        app.setApplicationName("Panther System Intelligence")
        app.setOrganizationName("Panther")

        # Step 3: Instantiate MainWindow
        log_startup("Instantiating MainWindow...")
        from .ui.main_window import MainWindow
        win = MainWindow()
        log_startup("MainWindow instantiated successfully.")

        # Step 4: Show and activate MainWindow
        log_startup("Calling win.show()...")
        win.show()
        win.raise_()
        win.activateWindow()
        log_startup(f"MainWindow displayed. isVisible={win.isVisible()}, geometry={win.geometry().getRect()}")

        # Step 5: Enter Qt event loop
        log_startup("Entering Qt event loop (app.exec())...")
        exit_code = app.exec()
        log_startup(f"Qt event loop finished with exit code: {exit_code}")
        return exit_code

    except Exception as e:
        tb = traceback.format_exc()
        log_startup(f"FATAL STARTUP EXCEPTION: {e}\n{tb}")
        print(f"FATAL ERROR:\n{tb}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
