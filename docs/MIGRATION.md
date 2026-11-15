# Migration: PySide6 -> React + Tailwind + Tauri

Source: `Atmos-A1/System-Management-Project@feature/storage-improvements` = `affe8ea17f1d54269eb1b6efc2db7bb824980a36` (unchanged at push time).
Target base `main` = `b997c3131e92bd62f7ebc7d9ba71ca10ae1d6f7a` (untouched).

## Moved to `legacy/pyside6`
The complete original tree at `affe8ea`: PySide6 UI, `run_panther.py`, `build_installer.py`, Qt tests, original CI.

## Removed from this branch
`src/panther/ui/`, `src/panther/main.py`, `run_panther.py`, `build_installer.py`, the `.lnk` shortcut, the PySide6 and pytest-qt requirements, all Qt-dependent test files, the PySide6 installer CI job and `QT_QPA_PLATFORM`.

## Retained
All of `src/panther/services`, `domain`, `config`, `db`, `logger`, `sidecar/`, `run_sidecar.py`, `build_sidecar.py`, and every non-Qt test. Nothing in the backend imported `panther.ui`.

## Adapted
- Startup: `set_startup_app_state` now fails closed in both directions; React toggle removed, screen explains it is read-only.
- Dashboard polling: next poll is scheduled only after the previous finishes (no overlapping requests); no loading flicker on refresh.
- Tauri: CSP set (was null); capability reduced to `core:default` (webview no longer has shell spawn); `invoke_metric` rejects method names not matching `system_monitor.[a-z0-9_]+`. Sidecar auth stays in Python.
- Added `@tauri-apps/cli`, `scripts/dev.ps1`, new README.

## Results (Linux container)
- Python: `pytest tests` -> 430 passed, 1 skipped, no PySide6 installed.
- Frontend: `tsc --noEmit` and `vite build` pass.
- Rust: `cargo fmt --check` clean; `cargo test` 25 passed.
- Windows CI (real windows-latest runner, run 43686826820 on f70e850): all steps passed: Python deps, sidecar tests, sidecar build and frozen-binary smoke test, tsc, Vite build, cargo check/test, NSIS build, silent install, graceful-shutdown and forced-kill orphan checks, uninstall. General CI and Tauri Linux CI also passed.
- Manual interactive launch on a developer Windows machine: not yet done.

## Incomplete
Audit found the frontend calls only the 18 registered `system_monitor.*` methods and these agree with the sidecar. Backend services without a sidecar method or React screen: duplicate detection/review, cleanup review/execution, file metadata/signature inspection, storage analysis/scan with progress and cancellation, process priority change and adaptive-control authorization flows beyond get/set. These were not implemented and are not faked. Process and storage safety code is unchanged and still tested.

## Security limitations
CSP allows `'unsafe-inline'` styles. Sidecar enforcement relies on the Python layer; Rust only validates method-name shape. The Tauri `dialog`, `fs`, `notification` and `shell` plugins are still initialised in Rust (not granted to the webview).
