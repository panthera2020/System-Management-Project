"""Process screen – displays a list of running processes.

A minimal read‑only QTableView is used. The data comes from the
:func:`panther.services.process_adapter.get_processes` adapter, which is
pure‑business‑logic and does not import any Qt classes. The UI component
only formats the data for display, keeping concerns separated.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex

from ..services.process_adapter import get_processes

class ProcessTableModel(QAbstractTableModel):
    def __init__(self, processes=None):
        super().__init__()
        self.headers = ["PID", "Name", "CPU %", "RAM (MiB)"]
        self._processes = processes or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._processes)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        proc = self._processes[index.row()]
        col = index.column()
        if col == 0:
            return proc.get("pid")
        if col == 1:
            return proc.get("name")
        if col == 2:
            return proc.get("cpu_percent")
        if col == 3:
            # Convert bytes to MiB for readability
            return f"{proc.get('memory_rss', 0) // (1024**2)}"
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return super().headerData(section, orientation, role)

class ProcessesScreen(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("processesScreen")
        layout = QVBoxLayout(self)
        self.table = QTableView()
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        # In a real app this would be called from a background worker.
        processes = get_processes()
        self.table.setModel(ProcessTableModel(processes))
        self.table.resizeColumnsToContents()
