# Phase 18 – React/Tauri Migration Handoff and Python 3.12 CI Regression

> Handoff document: `handoff_phase_18.md`
> Date: 2026-11-13
> Repository: `panthera2020/System-Management-Project`
> Main baseline at handoff: `6dbd31927563cc7f8f42293d6256e5994c70591d`
> Previous handoff: `handoff_phase_17.md`
> Scope: migration planning, CI investigation and current delivery status. No application source changes were made in this phase.

---

## 1. Executive Summary

The React + Tailwind + Tauri redesign has been accepted as a **presentation-layer migration**, not a rewrite of Panther's system logic.

The agreed architecture remains:

- **React + Tailwind:** presentation, navigation and user interaction.
- **Tauri + Rust:** desktop shell, lifecycle and controlled IPC.
- **Python:** authoritative system services, business rules, safety decisions, persistence and OS integration.

Existing functionality and safety guarantees must be preserved. No feature may be removed, weakened or represented as complete when it is only a placeholder. The legacy PySide6 application must not be retired until feature parity and Windows acceptance are demonstrated.

Two draft pull requests are currently open:

- **PR #2 – migration specification:** [docs: define React/Tauri feature-preservation migration contract](https://github.com/panthera2020/System-Management-Project/pull/2)
- **PR #3 – PySide6 dependency pin investigation:** [fix: stabilize PySide6 scan tests on Python 3.12](https://github.com/panthera2020/System-Management-Project/pull/3)

Neither PR is merged. PR #3's dependency pin did **not** resolve the Python 3.12 test failures. Do not describe the CI issue as fixed.

---

## 2. React/Tauri Migration Specification

### PR #2

- Branch: `docs/react-tauri-feature-preservation`
- Commit: `ecee7530fec5f31decb4471385cc8a4de13d15c0`
- File added: `docs/REDESIGN_MIGRATION_SPEC.md`
- Status: open, draft, not merged.
- CI run: [43446359234](https://github.com/panthera2020/System-Management-Project/actions/runs/43446359234) – failed.

The specification defines acceptance criteria and regression gates for Dashboard, Process/RAM, Storage, Battery, Startup Apps, Adaptive Control, Applications, Activity History, Settings, sidecar/IPC and packaging.

### Architecture and migration constraints

1. Python remains the source of truth for system behavior and safety.
2. React must call existing Python capabilities through a defined bridge; it must not reimplement system policy in TypeScript.
3. Rust owns desktop lifecycle and the controlled Python sidecar boundary.
4. Preserve persistence formats and existing workflows unless an explicit migration is designed and tested.
5. Do not retire the PySide6 launch/build path before React/Tauri feature parity, regression tests and Windows acceptance.
6. Known gaps must remain visibly incomplete; do not ship disabled controls as if the corresponding feature works.

### Known parity gaps from the React/Tauri review

- Storage UI does not yet demonstrate full Stage 3 parity: largest-file analysis, duplicate review, safe Recycle Bin cleanup, metadata/signature inspection, folder-size and file-type insights, scan history, progress and cancellation.
- Startup entry restoration/re-enable is incomplete. Deleting a registry entry without an exact reversible backup/restore path is not acceptable.
- Process UI is primarily read-only. Any future action must preserve identity verification and authorization; never act on PID alone.
- Adaptive Control UI is preference-oriented and does not establish that the enforcement engine is integrated.
- Settings need startup loading and real side effects for every setting presented as functional.
- Installed-app metadata contains fields that may be unavailable; show unavailable values rather than fabricated data.
- Dynamic Tailwind class construction may be purged; use static class maps or a safelist.
- Tauri CSP must be restrictive rather than null.
- Frontend tests and end-to-end coverage are not yet sufficient.
- Dashboard polling must avoid overlapping requests.

These are open review findings, not claims that the migration has already implemented or fixed them.

---

## 3. Python 3.12 / Qt Scan Test Failure

### Original CI failure – PR #2

Run: [43446359234](https://github.com/panthera2020/System-Management-Project/actions/runs/43446359234)

- Windows + Python 3.10: passed.
- Windows + Python 3.12: **428 passed, 4 failed, 2 skipped**.
- Packaging smoke test: skipped because the Python 3.12 test job failed.

The four failing tests were:

1. `tests/test_scan_controller.py::test_scan_runs_on_a_worker_thread_and_emits_progress`
2. `tests/test_scan_controller.py::test_duplicate_scan_hashes_on_worker_and_reports_hash_progress`
3. `tests/test_scan_controller.py::test_start_is_rejected_while_a_scan_is_active`
4. `tests/test_scan_lifecycle.py::test_actual_controller_to_storage_delivery`

The Qt event loop reported `OverflowError: int too big to convert`. The errors arise during the background Storage scan/Qt signal lifecycle. The exact root cause has **not** been established.

The original failing environment installed PySide6 6.12.0 because `requirements.txt` allowed any version `>=6.5.0`.

### Dependency-pin investigation – PR #3

- Branch: `fix/pyside6-312-qt-scan-tests`
- Commit: `2c8e45c10a46bd4e1fb1d084d3c5576e69898568`
- Change: pin `PySide6==6.11.2` in `requirements.txt`.
- Status: open, draft, not merged.
- CI run: [43447789291](https://github.com/panthera2020/System-Management-Project/actions/runs/43447789291) – completed with failure.

Results on the pin branch:

- Windows + Python 3.10: passed.
- Windows + Python 3.12: **428 passed, 4 failed, 2 skipped**.
- The same four scan/controller/lifecycle tests still fail with `OverflowError: int too big to convert`.
- Windows packaging smoke test: skipped because the Python 3.12 test job failed.

**Conclusion:** pinning PySide6 to 6.11.2 did not fix the failure. The hypothesis that PySide6 6.12.0 alone caused the problem is not supported by this rerun. Do not merge PR #3 as a verified fix. Reassess whether to retain the pin after the actual compatibility issue is understood.

### Required investigation

1. Retrieve complete Python 3.12 job logs and identify the exact Qt callback/signal/slot where the overflow originates.
2. Reproduce under the exact CI matrix on Windows, Python 3.12, with the installed PySide6, shiboken6 and pytest-qt versions recorded.
3. Inspect the worker-thread lifecycle, queued signal delivery, thread completion/deletion and Qt event-loop callbacks.
4. Check for Python integers being passed into Qt APIs that expect bounded C++ integer types (for example, timer intervals, wait timeouts or Qt integer properties). Do not assume this is the cause until the traceback identifies the call site.
5. Make the smallest behavior-preserving correction. Do not silence Qt exceptions, weaken assertions, skip the failing tests or move work back onto the UI thread.
6. Re-run the four focused tests, then the full suite on Python 3.10 and 3.12.
7. Require the Windows packaging smoke test to run and pass after the test matrix passes.

---

## 4. Storage Scan Implementation Context

The current `src/panther/ui/scan_controller.py` implementation uses:

- A dedicated `QThread` subclass to execute the worker.
- A worker-owned `FileScanner` and `DuplicateDetector`.
- Queued worker-to-controller signal connections.
- Generation identifiers to ignore stale signals.
- Cooperative cancellation.
- A module-level active-thread registry to keep running threads alive if a screen is destroyed.
- Bounded shutdown behavior.

The scanner reports progress and filesystem errors, does not follow symlinks/reparse points, and records device/inode identity for hardlink-aware duplicate handling.

The failing tests exercise the worker-thread progress path, duplicate hashing progress, active-scan rejection and delivery into `StorageScreen`. Preserve these behaviors while diagnosing the Qt failure.

---

## 5. Existing Product Safety and Functionality Constraints

The following earlier decisions remain binding:

- Process identity must not rely on PID alone; retain PID, creation time, executable and process name checks.
- Unknown or insufficiently verified processes fail closed.
- Protected/system-critical and foreground processes remain protected according to the existing authorization policy.
- No automatic process termination.
- Adaptive control remains disabled by default and must not silently apply actions.
- Resource changes require authorization, identity revalidation, verification and safe rollback.
- Storage cleanup remains default-deny and Recycle Bin-oriented. Revalidate exact file identity before cleanup.
- Partial, cancelled or errored scans must not become approved cleanup roots.
- Startup changes must not be exposed as reversible until exact source state is safely backed up and restored.
- No UI migration may weaken these protections.

Refer to `handoff_phase_16.md`, `handoff_phase_17.md` and `handoff_prd_alignment_and_remediation.md` for the detailed historical decisions and test requirements.

---

## 6. Current PR and CI Status

| Item | Current state |
|---|---|
| PR #1 – Stage 3 Storage merge | Previously merged; see Phase 17 |
| PR #2 – React/Tauri migration specification | Open, draft, not merged |
| PR #3 – PySide6 6.11.2 pin | Open, draft, not merged; does not fix Python 3.12 failures |
| Python 3.10 CI on PR #3 | Passed |
| Python 3.12 CI on PR #3 | Failed: 4 failed, 428 passed, 2 skipped |
| Windows packaging smoke test on PR #3 | Skipped |
| Root cause of Qt overflow | Unknown; investigation outstanding |
| React/Tauri feature parity | Not established |
| PySide6 retirement | Not authorized; do not remove legacy path |

No application source files were changed as part of the PR #2 documentation work or the PR #3 dependency-pin change.

---

## 7. Next Actions

1. Diagnose the precise Python 3.12 Qt overflow using the full traceback and a reproducible Windows run.
2. Fix the underlying issue without weakening scan behavior or tests.
3. Run focused scan tests, then the complete Python 3.10 and 3.12 suites.
4. Ensure the Windows packaging smoke test executes and passes.
5. Revisit PR #3's dependency pin based on evidence; do not treat it as the fix by itself.
6. Keep PR #2 as the migration contract and use its feature-by-feature acceptance criteria during implementation.
7. Continue React/Tauri work incrementally, preserving the Python backend and all existing safety rules.
8. Update this handoff with exact commits, test commands, environments and results after the next verified change.

---

## 8. Verification Commands

Run from the repository root on Windows:

```powershell
python -m pip install -r requirements.txt
python -m compileall -q src
python -m pytest -q -ra
```

For focused diagnosis:

```powershell
python -m pytest -q -ra tests/test_scan_controller.py tests/test_scan_lifecycle.py
```

Record the Python, PySide6, shiboken6, pytest and pytest-qt versions alongside every result.

**Release rule:** Do not mark the Qt issue resolved until the four regressions pass on Windows + Python 3.12, the full supported test matrix passes, and the packaging smoke test succeeds.
