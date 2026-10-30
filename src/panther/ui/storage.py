"""Storage screen – shows per-drive disk usage.

Queries psutil.disk_partitions() and disk_usage() for each mounted drive
and displays them in a simple table, refreshed on config.refresh_interval_seconds.
"""

import psutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QHBoxLayout,
)
from PySide6.QtCore import QTimer, Qt

from ..config import config


class StorageScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("storageScreen")
        layout = QVBoxLayout(self)

        title = QLabel("Storage – Disk Usage")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Drive", "Total", "Used", "Free"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.timer = QTimer(self)
        self.timer.setInterval(config.refresh_interval_seconds * 1000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh()

    def _fmt(self, b: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} PB"

    def refresh(self) -> None:
        partitions = []
        for p in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(p.mountpoint)
                partitions.append((p.mountpoint, usage))
            except PermissionError:
                continue

        self.table.setRowCount(len(partitions))
        for row, (mount, usage) in enumerate(partitions):
            self.table.setItem(row, 0, QTableWidgetItem(mount))
            self.table.setItem(row, 1, QTableWidgetItem(self._fmt(usage.total)))
            self.table.setItem(row, 2, QTableWidgetItem(
                f"{self._fmt(usage.used)} ({usage.percent:.0f}%)"
            ))
            self.table.setItem(row, 3, QTableWidgetItem(self._fmt(usage.free)))
