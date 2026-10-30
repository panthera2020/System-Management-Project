"""Panther System Intelligence UI – main window.

Provides a QMainWindow with a permanent left‑sidebar navigation list.
The central widget is a placeholder stacked widget that will host the
individual screens (Dashboard, Processes, …) once they are implemented.
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QLabel,
)
from PySide6.QtCore import Qt

from .navigation import NAV_ITEMS

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Panther System Intelligence")
        self.resize(1024, 720)

        # ----- layout ----------------------------------------------------
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Sidebar navigation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        for name, _icon in NAV_ITEMS:
            item = QListWidgetItem(name)
            self.sidebar.addItem(item)
        layout.addWidget(self.sidebar)

        # Stacked area for screens
        self.stack = QStackedWidget()
        # placeholder screens – just a label for now
        for name, _icon in NAV_ITEMS:
            if name == "Dashboard":
                from ..dashboard import DashboardScreen
                widget = DashboardScreen()
            elif name == "Startup Apps":
                from ..ui.startup import StartupScreen
                widget = StartupScreen()
            else:
                placeholder = QLabel(f"{name} screen – not implemented yet")
                placeholder.setAlignment(Qt.AlignCenter)
                widget = placeholder
            self.stack.addWidget(widget)
        layout.addWidget(self.stack)

        # Connect navigation
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)
