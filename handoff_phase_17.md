# Phase 17 – Stage 3 Storage Merge, Cross-Branch Fixes and Review Findings

> Handoff document: `handoff_phase_17.md`
> Baseline: `main` @ `e586885` ("fixes")
> Result: `main` @ `e5b258a` ("Merge PR #1 (Stage 3 storage) with process, history and monitor fixes")
> Previous handoff: `handoff_phase_16.md` (PAPC foundation). Stage 3 detail: `docs/handover/STAGE_3_HANDOVER.md`.

---

## 1. Executive Summary

`main` now contains the Stage 3 Storage subsystem (PR #1, GitHub user `Atmos-A1`, commits authored as "Honour") **and** a set of independent fixes made on `claude/fix-process-tests-and-safety`. The two were merged on `claude/merge-pr1-with-fixes` and fast-forwarded into `main` (`e586885..e5b258a`). PR #1 shows as merged on GitHub.

- Full suite: **434 passed** (Linux, Python 3.13, PySide6 6.12.0, `QT_QPA_PLATFORM=offscreen`), source compiles, all ten screens construct and render headless.
- **Not yet validated on Windows.** See section 6.

---

## 2. What Is In `main` Now

### From PR #1 (Stage 3 storage, `1d59397` head)
- Stage 3A–3E: read-only Storage Explorer, folder-size and file-type insights, metadata and file-signature inspection, model-backed filtering for large results, scan-history filtering and pagination.
- Cleanup hardening: default-deny, Recycle Bin/trash only, `permanent_delete` raises `PermissionError`, symlink/reparse-point rejection (target and ancestors), approved scan roots, per-file identity check `(st_dev, st_ino, st_size, st_mtime_ns)` captured at review and re-checked immediately before trashing. Partial, cancelled and errored scans leave no approved root, so they cannot become cleanup targets.
- Test-database isolation (`tests/conftest.py`, `tests/test_test_isolation.py`).
- Dashboard card layout fix with per-card regression tests.
- GitHub Actions CI (`.github/workflows/ci.yml`): Windows, Python 3.10 and 3.12, plus a Windows packaging smoke test. `requires-python` is now `>=3.10`.

### From `claude/fix-process-tests-and-safety`
- `ProcessesScreen` accepts an injected `process_classifier` (the PID-reuse test no longer depends on the OS account and install path).
- Settings → **Clear Activity History** now deletes rows (`history.clear_history()`); it previously only showed a success message.
- Critical process names are lower-cased so `RuntimeBroker.exe` and `SearchIndexer.exe` can match.
- `system_monitor`: non-blocking CPU reads (primed at import); disk default is the system drive (`SystemDrive`) instead of a hard-coded `C:\`, with a root fallback off Windows.
- `history.record_event` no longer uses deprecated `utcnow()` (stored format unchanged: naive UTC ISO).
- `Send2Trash` declared in `requirements.txt`, `pyproject.toml` and the PyInstaller `--hidden-import` list.
- Dashboard labels are transparent so they no longer tint the white cards.

### New in the merge
- **Hardlinks are no longer counted as duplicate copies.** `FileScanner` records `device` and `inode`; `DuplicateDetector` counts each on-disk file once. Before: file + hardlink + copy reported 10,000 bytes of savings; correct is 5,000. Tests: `tests/test_duplicate_hardlinks.py` (three of five fail without the fix).

---

## 3. Conflict Resolution Decisions

| File | Decision | Reason |
| --- | --- | --- |
| `services/cleanup_manager.py` | PR version | Stricter default-deny design supersedes the simple protected-path guard. |
| `services/file_scanner.py` | PR version + `device`/`inode` fields | PR adds cancellation, progress and reparse handling. |
| `services/duplicate_detector.py` | PR version + hardlink dedupe | Same. |
| `tests/test_ui_dashboard.py` | PR version | More thorough per-card tests; mine were redundant. |
| `tests/test_storage_services.py` (mine) | Removed | Targeted the superseded cleanup API; PR suites cover those rules. |

---

## 4. Defects Found During This Phase

1. **Dashboard cards showed only titles** (introduced in `e586885`). An early `return card` in `DashboardScreen.create_card` made the value, detail and progress widgets unreachable. Fixed independently on both branches; PR tests now guard it. The old dashboard test passed despite the bug because the labels existed as attributes but were never placed in the card.
2. **Hardlink overcounting** in duplicate results (section 2).
3. **PID-reuse test failure** was a test bug: the classifier now only labels a process "User application" when it runs as the current OS user from Program Files or AppData, so the fixture row was hidden by the filter.
4. A stale `dist\PantherApp\PantherApp.exe` is built from older source. Test from source (`python run_panther.py`) or rebuild (`python build_installer.py`).

---

## 5. Review Findings on PR #1 (verified)

Probed directly: cleanup rejects no-root, outside-root, symlink target, path through a symlinked directory and a file changed since review (file left untouched); `permanent_delete` raises; the UI passes reviewed identities into `move_to_recycle_bin`. Test changes in the "fix CI failures" commit did not weaken coverage (one assertion made platform-conditional, one `xfail` removed).

**Authorship note:** the roughly 8,000-line Stage 3 implementation is a single commit (`8ebcf6e`) authored as "Panther Developer <developer@panther.local>" on 2 Nov 2026, before the PR author's first commit. The PR description attributes the whole stage to its author. Confirm provenance if it matters for credit.

---

## 6. Verification Status

| Item | Status |
| --- | --- |
| Full test suite (Linux) | 434 passed, 0 skipped |
| `python -m compileall -q src` | Passed |
| Headless render of all ten screens | Passed, no errors |
| GitHub Actions results (Windows 3.10, 3.12, packaging) | **Not verified** by this phase; the check-runs API was not reachable. PR author reports all three passed. |
| Real Windows run (tests + manual smoke) | **Outstanding** |
| Packaged `.exe` actually launches | **Outstanding** (CI only checks that the file exists) |
| Hardlink identity on Windows (`st_ino` populated for NTFS) | **Unconfirmed**; believed correct |

The Windows checklist in `docs/handover/STAGE_3_HANDOVER.md` section E remains the release gate and is unchanged.

---

## 7. Open Items And Known Limitations

Behaviour that is strict by design but may surprise users:
- Any scan error marks the scan partial and disables cleanup for it; large user-profile scans on Windows will often hit a permission error.
- `%USERPROFILE%\AppData` is protected, so temp and cache files cannot be cleaned.
- The Processes screen only lists processes owned by the current user that run from Program Files or AppData; apps installed elsewhere (for example another drive) are hidden.
- Reparse points are skipped by the scanner. This probably includes OneDrive online-only placeholders, which would undercount storage (unverified on Windows).

Unfinished work:
- Enabling a startup entry still raises `NotImplementedError` (`startup_adapter.set_entry_enabled`); the original command must be stored before deletion.
- Legacy `services/process_actions.py` (`psutil.terminate()`, in-memory audit log) is still used by the Battery screen's kill buttons. They are dormant because nothing is classified terminable, but they conflict with the identity-checked graceful-close and force-stop services and should be removed or rewired before process actions are enabled.
- Recommendation engine fires on a single sample and uses fixed confidence values; no dismissal or links to detail screens (PRD 5.7).
- CI packaging smoke test only asserts the executable exists. A headless smoke test that constructs `MainWindow` and visits every screen (about one second) would catch blank-startup regressions.
- Adaptive Control placeholder text is very low contrast.
- `QSortFilterProxyModel.invalidateFilter()` deprecation warning in `ui/processes.py`.
- Repository hygiene: `Panther System Intelligence.lnk`, `Panther_System_Intelligence_PRD.docx` and `prd_extracted.txt` are tracked; the README is empty.

---

## 8. Statements In Earlier Handoffs That Are Now Out Of Date

- `STAGE_3_HANDOVER.md` section D, "Known unrelated failure" (`DashboardScreen` has no `cpu_label`): resolved; the aliases exist and the dashboard is covered by tests.
- `STAGE_3_HANDOVER.md` section F item 1 (test environment lacked `send2trash`): the dependency is now declared everywhere; Recycle Bin movement is still only mocked in tests.
- Test counts in earlier handoffs (266, 123) are superseded by 434.

---

## 9. How To Verify

```
git checkout main
git pull
python -m pip install -r requirements.txt
python -m pytest -q          # expect 434 passed
python run_panther.py        # launch from source, not the old dist build
```

Manual checks: dashboard cards show values and bars; Storage has six tabs (Overview, Largest Files, Duplicates, Explorer, Insights, Scan History); duplicate savings are not inflated by hardlinks; Clear Activity History empties the history screen.
