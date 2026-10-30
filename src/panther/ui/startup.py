"""Startup screen – shows Run‑key entries.

The UI builds a read‑only table of startup entries (name, command, scope).
All heavy work is delegated to :func:`panther.services.startup_adapter.get_startup_entries`.
A placeholder "Disable" button is shown per row but does not perform any action –
the destructive toggle will be wired later with a confirmation dialog.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton, QHBoxLayout
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

from ..services.startup_adapter import get_startup_entries

class StartupTableModel(QAbstractTableModel):
    def __init__(self, entries=None):
        super().__init__()
        self.headers = ["Name", "Command", "Scope"]
        self._data = entries or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        entry = self._data[index.row()]
        col = index.column()
        if col == 0:
            return entry.get("name")
        if col == 1:
            return entry.get("command")
        if col == 2:
            return entry.get("scope")
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

class StartupScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("startupScreen")
        layout = QVBoxLayout(self)
        self.table = QTableView()
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        entries = get_startup_entries()
        self.table.setModel(StartupTableModel(entries))
        self.table.resizeColumnsToContents()
