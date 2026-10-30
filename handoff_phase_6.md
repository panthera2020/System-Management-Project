# Phase 6 – Startup & Application Management Hand‑off

**What was added**
- `services/startup_adapter.py` – pure‑logic service that reads Windows Run‑key entries (HKCU & HKLM) and provides a `set_entry_enabled` stub (disable only, enable not implemented yet). No UI imports, preserving separation of concerns.
- `ui/startup.py` – UI screen with a read‑only table of startup entries and a placeholder for future enable/disable actions. Uses the service adapter for data.
- `services/battery_adapter.py` – thin wrapper around `psutil.sensors_battery` returning a dict (or empty dict when no battery). Pure business logic.
- `ui/battery.py` – UI screen that displays battery percent, charging state, and time‑left, updating via a `QTimer` based on the config refresh interval.
- Unit tests: `tests/test_startup_adapter.py` (registry mock) and `tests/test_battery_adapter.py` (psutil mock).

**PRD excerpt** (relevant to this phase):
> *Startup and Background Manager*: inspect supported startup folders, registry Run entries, scheduled tasks and services. Show name, publisher, executable path, source, associated application and available startup impact evidence. Distinguish disabling a startup entry from uninstalling an app or stopping a service. Allow supported startup entries to be enabled or disabled with confirmation and audit history. Do not disable services automatically.

> *Battery and Power Intelligence*: show battery charge, charging/discharging state and estimated runtime when supplied by Windows. Show design capacity and full‑charge capacity when available; derive a clearly labelled health estimate only when data is reliable. Collect supported system power information and available Windows application power attribution. Correlate process CPU, disk, network and background activity with observed system discharge trends. Show high, moderate or low estimated impact only when sufficient evidence exists. Label measured values, Windows‑provided estimates and application‑derived estimates distinctly.

---
*The hand‑off file is committed alongside the code changes for Phase 6.*
