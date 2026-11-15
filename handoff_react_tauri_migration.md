# Handoff: React + Tailwind + Tauri migration

## State
- Repo: panthera2020/System-Management-Project
- `legacy/pyside6` = affe8ea17f1d54269eb1b6efc2db7bb824980a36 (original PySide6, from Atmos-A1 feature/storage-improvements, unchanged)
- `feature/react-tauri-desktop` = f70e850412238b1566c111c5273751e878bfa5f2 (plus any later handoff commit)
- `main` = b997c31, untouched. Nothing merged, no force-pushes.

## Done
- Removed Qt UI, `main.py`, `run_panther.py`, `build_installer.py`, Qt tests, PySide6 and pytest-qt deps. Backend, sidecar, services untouched.
- Startup apps read-only (sidecar `set_startup_app_state` fails closed; React toggle removed).
- Dashboard polling serialised (setTimeout after completion, cleanup on unmount).
- Tauri: CSP set, capability reduced to `core:default`, `invoke_metric` validates `system_monitor.[a-z0-9_]+`.
- `scripts/dev.ps1`, `@tauri-apps/cli` dev dependency, README, `docs/MIGRATION.md`, CI without Qt.

## Verified
- Linux: pytest 430 passed / 1 skipped; tsc and Vite build pass; cargo fmt clean; cargo test 25 passed.
- Windows CI (run 43686826820): all steps green including NSIS build, silent install, orphan checks, uninstall.
- Not verified: manual interactive launch via `scripts\dev.ps1` on a real Windows machine.

## Not done (next work)
Backend services exist but have no sidecar method or React screen:
1. File metadata and signature inspection (read-only; do first).
2. Duplicate detection and review (never auto-delete).
3. Storage scan with progress and cancellation; cancelled/errored scans must never become approved cleanup roots.
4. Cleanup review and execution (default-deny, Recycle Bin, revalidate file identity).
5. Process priority control (PID + creation time + path + name identity, authorization service, verify and roll back, REALTIME blocked, adaptive control off by default).
Method: add sidecar method in `src/panther/sidecar/methods/` and register in its `__init__.py`, add tests, then the React screen via `invokeMetric`. Never reimplement rules in React or Rust; no mock data.

## Also open
- Audit remaining screens (processes, settings persistence, applications) for schema agreement and honest success/error states.
- CSP still allows `'unsafe-inline'` styles.
- Open to add: frontend unit tests for IPC wrapper.

## Commands
Tests: `$env:PYTHONPATH="src"; python -m pytest tests -q --timeout=120`; frontend `npx tsc --noEmit; npm run build` in `src-tauri\frontend`; Rust `cargo fmt --check; cargo test` in `src-tauri`.
Run: `powershell -ExecutionPolicy Bypass -File scripts\dev.ps1`.
Note: local checkout is shallow; push with `git -c push.negotiate=true push`.
