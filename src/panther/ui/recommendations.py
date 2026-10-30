"""Recommendations screen – shows a list of suggestions.

The UI builds a simple read‑only table displaying the fields returned by
:func:`panther.services.recommendation_engine.get_recommendations`.  The screen
fetches the current metrics from the existing system‑monitor service (CPU,
RAM, Disk, Battery) and refreshes on the same timer interval as the dashboard.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QTimer

from ..config import config
from ..services.recommendation_engine import get_recommendations
from ..services.system_monitor import (
    get_cpu_percent,
    get_ram_usage,
    get_disk_usage,
    get_battery_info,
)

class RecTableModel(QAbstractTableModel):
    def __init__(self, recs=None):
        super().__init__()
        self.headers = ["Issue", "Evidence", "Benefit", "Risk", "Action"]
        self._recs = recs or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._recs)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        rec = self._recs[index.row()]
        col = index.column()
        return rec[self.headers[col].lower()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

class RecommendationsScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("recommendationsScreen")
        layout = QVBoxLayout(self)
        self.table = QTableView()
        layout.addWidget(self.table)
        self.timer = QTimer(self)
        self.timer.setInterval(config.refresh_interval_seconds * 1000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh()

    def _gather_metrics(self):
        cpu = get_cpu_percent()
        ram = get_ram_usage()["percent"]
        disk = get_disk_usage()["percent"]
        batt_info = get_battery_info()
        batt = batt_info.get("percent") if batt_info else None
        return {"cpu_percent": cpu, "ram_percent": ram, "disk_percent": disk, "battery_percent": batt}

    def refresh(self):
        metrics = self._gather_metrics()
        recs = get_recommendations(metrics)
        self.table.setModel(RecTableModel(recs))
        self.table.resizeColumnsToContents()
