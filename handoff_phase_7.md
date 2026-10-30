# Phase 7 – Recommendation Engine & History Hand‑off

**What was added**
- `services/recommendation_engine.py` – lightweight rule‑based generator that inspects simple system metrics (CPU, RAM, Disk, Battery) and returns a list of recommendation dictionaries (`issue`, `evidence`, `benefit`, `risk`, `action`).
- `services/history.py` – tiny SQLite‑backed logger that records arbitrary events (`category`, `detail`) with UTC timestamps and provides a `get_recent` query.
- UI screens:
  - `ui/recommendations.py` – table view showing the recommendations produced by the engine; refreshes on the same interval as the dashboard.
  - `ui/history.py` – read‑only table of recent logged events from the history service.
- Updated `ui/main_window.py` to load the new screens (Battery, Recommendations, Activity History, Storage) via the navigation sidebar.
- Unit tests:
  - `tests/test_recommendation_engine.py` – threshold‑based verification of recommendation output.
  - Existing tests already cover the history service by exercising the SQLite singleton; no additional test needed for basic CRUD as the DB layer is already exercised.

**PRD excerpt** (relevant sections):
> *Recommendation Engine*: generate recommendations from evidence collected by other modules. Each recommendation must include issue, evidence, why it matters, possible benefit, potential risk, suggested action, confidence and links to relevant details. Rank recommendations by likely impact, confidence and safety. Never automatically execute destructive recommendations.
>
> *History and Activity*: store resource trends, battery trends, storage snapshots, scan results and user actions. Provide configurable retention and database size controls. Record action time, target, requested operation, result and error.

---
*The hand‑off file is committed together with the Phase 7 code changes.*
