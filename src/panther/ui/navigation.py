"""Navigation definitions for the sidebar.
Provides a constant ``NAV_ITEMS`` – a list of tuples ``(name, icon_path)``.
Icons are optional; we use placeholder empty strings for now.
"""

# Order matters – used by ``MainWindow`` to build the sidebar
NAV_ITEMS = [
    ("Dashboard", ""),
    ("Processes", ""),
    ("Startup Apps", ""),
    ("Battery", ""),
    ("Recommendations", ""),
    ("Activity History", ""),
    ("Storage", ""),
]
