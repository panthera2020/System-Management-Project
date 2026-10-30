"""Battery screen – shows power status.

A lightweight UI that queries :func:`panther.services.battery_adapter.get_battery_status`
and displays percent, charging state, and time‑left. The widget updates on a
QTimer using the refresh interval from the config. No direct OS calls are
made here – the service layer handles that, preserving separation of concerns.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import QTimer, Qt

from ..config import config
from ..services.battery_adapter import get_battery_status

class BatteryScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("batteryScreen")
        layout = QVBoxLayout(self)
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.timer = QTimer(self)
        self.timer.setInterval(config.refresh_interval_seconds * 1000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh()

    def refresh(self) -> None:
        batt = get_battery_status()
        if not batt:
            self.info_label.setText("No battery detected")
            return
        percent = batt["percent"]
        charging = "Charging" if batt["power_plugged"] else "Discharging"
        secs = batt["secsleft"]
        if secs == -2:
            time_left = "unknown"
        elif secs == -1:
            time_left = "unlimited"
        else:
            hrs, rem = divmod(secs, 3600)
            mins = rem // 60
            time_left = f"{hrs}h {mins}m"
        self.info_label.setText(f"{percent}% – {charging} – {time_left}")
