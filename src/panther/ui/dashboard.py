"""Dashboard screen – shows RAM, CPU, Disk and Battery summary cards.

Each card is a simple QLabel that displays the latest reading.
Updates are performed in a background QTimer (interval from config).
Business logic (data retrieval) lives in :mod:`panther.services.system_monitor`.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QGridLayout
from PySide6.QtCore import QTimer, Qt

from ..config import config
from ..services.system_monitor import (
    get_cpu_percent,
    get_ram_usage,
    get_disk_usage,
    get_battery_info,
)

class DashboardScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("dashboardScreen")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Create group boxes for each metric
        self.cpu_label = QLabel()
        self.ram_label = QLabel()
        self.disk_label = QLabel()
        self.battery_label = QLabel()

        grid = QGridLayout()
        grid.addWidget(self._group("CPU", self.cpu_label), 0, 0)
        grid.addWidget(self._group("RAM", self.ram_label), 0, 1)
        grid.addWidget(self._group("Disk", self.disk_label), 1, 0)
        grid.addWidget(self._group("Battery", self.battery_label), 1, 1)
        layout.addLayout(grid)

        # Timer for periodic refresh
        self.timer = QTimer(self)
        self.timer.setInterval(config.refresh_interval_seconds * 1000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh()  # initial load

    def _group(self, title: str, label: QLabel) -> QGroupBox:
        box = QGroupBox(title)
        box_layout = QVBoxLayout()
        label.setAlignment(Qt.AlignCenter)
        box_layout.addWidget(label)
        box.setLayout(box_layout)
        return box

    def refresh(self) -> None:
        # CPU
        cpu = get_cpu_percent()
        self.cpu_label.setText(f"{cpu:.1f}%")
        # RAM
        ram = get_ram_usage()
        self.ram_label.setText(
            f"{ram['used'] // (1024**2)} MiB / {ram['total'] // (1024**2)} MiB ({ram['percent']:.0f}%)"
        )
        # Disk (root)
        disk = get_disk_usage()
        self.disk_label.setText(
            f"{disk['used'] // (1024**3)} GiB / {disk['total'] // (1024**3)} GiB ({disk['percent']:.0f}%)"
        )
        # Battery
        batt = get_battery_info()
        if batt:
            self.battery_label.setText(
                f"{batt['percent']:.0f}% "
                + ("(Charging)" if batt["power_plugged"] else "(Discharging)")
            )
        else:
            self.battery_label.setText("No battery detected")
