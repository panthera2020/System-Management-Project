"""Panther System Intelligence UI – main window.

Provides a QMainWindow with a permanent left-sidebar navigation list.
The central widget is a stacked widget that hosts all screens.
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
from .dashboard import DashboardScreen
from .processes import ProcessesScreen
from .startup import StartupScreen
from .battery import BatteryScreen
from .recommendations import RecommendationsScreen
from .history import HistoryScreen
from .storage import StorageScreen


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Panther System Intelligence")
        self.resize(1024, 720)

        # ----- layout --------------------------------------------------------
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

        _screen_map = {
            "Dashboard": DashboardScreen,
            "Processes": ProcessesScreen,
            "Startup Apps": StartupScreen,
            "Battery": BatteryScreen,
            "Recommendations": RecommendationsScreen,
            "Activity History": HistoryScreen,
            "Storage": StorageScreen,
        }

        for name, _icon in NAV_ITEMS:
            cls = _screen_map.get(name)
            if cls is not None:
                widget = cls()
            else:
                placeholder = QLabel(f"{name} screen – coming soon")
                placeholder.setAlignment(Qt.AlignCenter)
                widget = placeholder
            self.stack.addWidget(widget)

        layout.addWidget(self.stack)

        # Connect navigation
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)
