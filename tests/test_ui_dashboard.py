import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication
from panther.ui.dashboard import DashboardScreen

@pytest.fixture(scope="module")
def app():
    # Ensure a QApplication exists for the test session
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

def test_dashboard_loads(app):
    # Simply instantiate the widget; refresh will be called automatically
    widget = DashboardScreen()
    assert widget.objectName() == "dashboardScreen"
    # Basic sanity: labels contain non‑empty text after refresh
    widget.refresh()
    assert widget.cpu_label.text() != ""
    assert widget.ram_label.text() != ""
    assert widget.disk_label.text() != ""
    # Battery may be absent, but label should be set
    assert widget.battery_label.text() != ""
