"""Application entry point for Panther.

Running this module starts the Qt event loop and shows the main window.
All heavy work is delegated to background workers in later phases.
"""

import sys
from PySide6.QtWidgets import QApplication
from .ui.main_window import MainWindow
from .logger import get_logger

def main() -> None:
    logger = get_logger(__name__)
    logger.info("Starting Panther System Intelligence UI")
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
