"""History screen – displays recent logged events.

Uses the :func:`panther.services.history.get_recent` service to fetch the most
recent rows from the SQLite ``history`` table and shows them in a read‑only
table.  The screen refreshes on the same interval as the dashboard.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QTimer

from ..config import config
from ..services.history import get_recent

class HistoryTableModel(QAbstractTableModel):
    def __init__(self, rows=None):
        super().__init__()
        self.headers = ["ID", "Timestamp", "Category", "Detail"]
        self._rows = rows or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._rows[index.row()]
        col = index.column()
        return row[col]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

class HistoryScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("historyScreen")
        layout = QVBoxLayout(self)
        self.table = QTableView()
        layout.addWidget(self.table)
        self.timer = QTimer(self)
        self.timer.setInterval(config.refresh_interval_seconds * 1000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh()

    def refresh(self):
        rows = get_recent(100)
        self.table.setModel(HistoryTableModel(rows))
        self.table.resizeColumnsToContents()
