# React + Tailwind + Tauri Redesign — Feature Preservation and Migration Contract

**Status:** Required migration gate  
**Target UI:** React + TypeScript + Tailwind CSS  
**Desktop host:** Tauri 2 + Rust  
**Authoritative system layer:** Existing Panther Python services  
**Scope:** Replace the presentation layer without regressing existing capabilities.

---

## 1. Non-negotiable rule

The redesign is a **frontend and desktop-shell migration**, not a rewrite of Panther's system-management logic.

React must not duplicate or replace Python business rules. Tauri/Rust must expose a narrow, typed bridge to existing Python services. Existing Python services remain authoritative for system discovery, policy decisions, safety checks, persistence and operating-system actions.

No feature may be silently removed, weakened, represented as functional when it is only a preference, or replaced by a placeholder. A feature that is not yet supported by the new interface must remain available through the old application during the transition, or be explicitly marked as not yet migrated. The old application must not be retired until the release gates in this document pass.

### Architecture contract

```text
React + TypeScript + Tailwind
             |
             | typed commands / typed results
             v
       Tauri 2 / Rust
             |
             | allowlisted JSON-RPC over sidecar stdin/stdout
             v
       Python sidecar / API
             |
             v
 Existing Panther services, domain rules and persistence
             |
             v
        Windows APIs / OS
```

- React owns rendering, navigation, view state, accessible interaction and presentation.
- Rust owns desktop lifecycle, command validation, sidecar lifecycle, IPC and error translation.
- Python owns system-management behaviour, policy, safety, domain decisions and data access.
- The bridge must not expose arbitrary Python evaluation, shell execution, arbitrary filesystem deletion or unrestricted process control.
- UI code must never bypass authorization by calling Windows APIs or invoking a weaker legacy action path directly.

## 2. Baseline inventory and acceptance criteria

The following is the migration checklist. “Preserve” means retain the existing service behaviour and data contract, not merely display a visually similar screen.

### 2.1 Dashboard and system monitoring

**Existing responsibility:** Present live system health and resource summaries from the system-monitoring layer.

Acceptance tests:
- [ ] Dashboard loads CPU, memory/RAM, storage and battery values from the authoritative backend; it does not fabricate values.
- [ ] Unavailable metrics are displayed as unavailable, not as a real zero.
- [ ] Units, percentages and capacity values are consistent with backend values.
- [ ] Loading, stale-data, partial-data and backend-error states are distinguishable.
- [ ] Polling cannot overlap indefinitely; slow requests do not create an unbounded queue.
- [ ] Navigating away cancels or safely ignores stale responses.
- [ ] A failed refresh does not erase the last known good snapshot without clearly labelling it stale.
- [ ] Dashboard totals and individual screens use the same source and compatible sampling windows.

### 2.2 Process and RAM Management

**Existing responsibility:** Discover and display processes, classify candidates, expose resource usage and enforce strict authorization boundaries.

Version 1 scope remains application-focused: show only eligible user-application candidates in the default view. Advanced visibility of system/background categories is deferred to Version 2.

Acceptance tests:
- [ ] Process discovery remains off the UI thread and supports incremental/batched results.
- [ ] UI identity is based on the full `ProcessIdentity` (PID + creation time + executable + process name), not PID alone.
- [ ] PID reuse clears stale selection and never carries an action decision to a different process instance.
- [ ] CPU baselines, missing values, inaccessible processes and disappearing processes are represented accurately.
- [ ] Search, filtering, sorting and refresh preserve the existing user-application-only v1 scope.
- [ ] Unknown, unverified, protected, system-critical and Panther processes remain blocked from actions.
- [ ] Classification is never treated as authorization.
- [ ] Any future graceful-close action requires fresh identity verification, trusted identity-bound evidence, explicit user confirmation, a background worker, exit verification and structured action history.
- [ ] Timeout or failure never escalates silently to force termination.
- [ ] Force Stop remains unavailable unless separately specified, reviewed and tested.
- [ ] No UI control is enabled unless the backend operation is implemented and its safety gate passes.
- [ ] Process list refresh and scrolling remain responsive under a realistic process count.

**Important current limitation:** The documented graceful-close service has an outstanding production acceptance gate, including a trusted evidence provider, UI worker/confirmation integration, action history and real Windows validation. The redesign must not imply that process closing is production-ready until those gates are completed.

### 2.3 Storage management

**Existing responsibility:** Inspect disks and directories and provide safe file-level intelligence and cleanup workflows.

Acceptance tests:
- [ ] Disk/volume usage and directory navigation still work with the same path and permission semantics.
- [ ] Largest-file discovery is retained, including size ordering and path identity.
- [ ] Duplicate detection preserves the existing hashing/equivalence rules and hard-link handling.
- [ ] Duplicate review remains review-first; the UI does not automatically delete duplicate candidates.
- [ ] File metadata and signature inspection retain existing fields and error handling.
- [ ] Folder-size and file-type summaries match backend calculations.
- [ ] Scan progress, cancellation and partial/error states are visible where the backend supports them.
- [ ] Scan history remains available where persisted by the current implementation.
- [ ] Cleanup policy remains deny-by-default for protected/system paths and respects existing exclusions.
- [ ] Recycle Bin or reversible cleanup behaviour is preserved; permanent deletion is never substituted silently.
- [ ] Cleanup preview, user confirmation, operation result and failure details are retained.
- [ ] A failed cleanup leaves a truthful result and does not report success.
- [ ] Large scans do not block the React UI or Tauri command loop.

**Required parity areas:** largest files, duplicate detection/review, safe Recycle Bin cleanup, file metadata/signature inspection, folder-size insights, file-type analysis, scan history, progress and cancellation. A screen that only calls disk usage and directory listing does not satisfy Storage parity.

### 2.4 Battery

Acceptance tests:
- [ ] Battery presence, charge level, charging state, remaining-time estimate and health/diagnostic fields are shown only when the backend provides them.
- [ ] Unsupported or desktop/no-battery systems show a clear not-applicable state.
- [ ] Battery recommendations are traceable to measured values and do not claim that a setting has been applied when it has not.
- [ ] Battery data refreshes without blocking the UI.
- [ ] Existing battery adapter tests continue to pass.

### 2.5 Startup applications

Acceptance tests:
- [ ] Startup entries are discovered with their source, command/path and current enabled state.
- [ ] A disable action is only exposed when a safe restore/backup path exists.
- [ ] Re-enable restores the exact prior entry, including original registry value/command and relevant metadata.
- [ ] Failed modifications are rolled back or reported as incomplete.
- [ ] Each mutation requires an explicit user action and confirmation.
- [ ] The UI never presents an irreversible delete as a reversible enable/disable toggle.

**Important current limitation:** The existing adapter's enable path is not implemented, and disabling by deleting a registry value is not inherently reversible. Until a tested backup/restore implementation exists, the new UI must be read-only for these entries or expose only the exact safe operations already supported. Do not render a working-looking toggle.

### 2.6 Adaptive Process Controller

Acceptance tests:
- [ ] Existing adaptive policy engine rules and thresholds remain unchanged during the UI migration.
- [ ] Current policy preferences are loaded and saved through the backend, with validation and persistence tests.
- [ ] The UI distinguishes saved preferences from active enforcement.
- [ ] No claim of active resource enforcement is made unless the actual resource controller is connected, enabled under the agreed policy and returning verified outcomes.
- [ ] Adaptive control remains disabled by default unless the product's approved safety design explicitly changes that.
- [ ] Foreground/active workload protection, system-process protection, identity revalidation and rollback behaviour remain enforced.
- [ ] Failed or rejected changes are surfaced; the UI never reports a preference save as a successful system action.

**Important current limitation:** A preference-only adapter/UI is not equivalent to active adaptive resource control. Preserve the current policy layer, but label enforcement as unavailable until it is genuinely wired and tested.

### 2.7 Installed applications

Acceptance tests:
- [ ] Installed-application discovery and search remain backed by the existing source.
- [ ] Missing metadata (for example, install date or resource fields not supplied by the backend) remains unknown rather than invented.
- [ ] Empty, inaccessible and partially discovered application inventories have distinct states.
- [ ] The redesign does not imply install/uninstall capability unless implemented and authorized.

### 2.8 Activity history

Acceptance tests:
- [ ] Existing persisted activity records remain readable after upgrade.
- [ ] Ordering, timestamps, event types and result/status details are preserved.
- [ ] Empty history is distinct from a read failure.
- [ ] Pagination or incremental loading does not omit or duplicate records.
- [ ] Any clear-history operation requires explicit confirmation and is only shown if implemented by the backend.
- [ ] UI formatting does not mutate or discard stored history.

### 2.9 Settings and preferences

Acceptance tests:
- [ ] Existing saved settings survive application upgrade and migration.
- [ ] Settings are loaded once during application startup and applied consistently across all screens.
- [ ] Theme changes apply immediately and persist across restart.
- [ ] Every visible setting has a documented effect and a test proving that effect.
- [ ] Settings that are not implemented are hidden or explicitly marked unavailable; they must not appear as functional toggles.
- [ ] Auto-start, notifications, update checks, telemetry, compact mode and language are only presented as active controls if their corresponding behaviour exists.
- [ ] Save failures are visible and do not falsely update the persisted state.
- [ ] Defaults and backward compatibility are covered by migration tests.

### 2.10 Desktop lifecycle, sidecar and packaging

Acceptance tests:
- [ ] Tauri starts the intended Python sidecar reliably on supported Windows versions.
- [ ] Sidecar stdout contains protocol messages only; logs go to stderr or the application logger.
- [ ] Startup timeout, crash, malformed response, EOF and restart paths produce useful errors.
- [ ] Application exit terminates the child process and leaves no orphan sidecar.
- [ ] Repeated launch/close cycles do not leak processes, handles or files.
- [ ] IPC is allowlisted and validates arguments and response shapes.
- [ ] Tauri capabilities are least-privilege; the webview has a restrictive Content Security Policy.
- [ ] User data, settings and history remain in stable locations and are not lost during installation/update.
- [ ] Windows installer installs, launches, upgrades and uninstalls cleanly.
- [ ] The official release path is unambiguous. PySide6 may remain during transition, but there must be one declared production entry point and no accidental split between two competing installers.

## 3. Cross-cutting bridge contract

Every command must have:
1. A stable command name and typed input schema.
2. A typed success response.
3. A typed error response with a safe, user-presentable message and machine-readable code.
4. Input validation at the Rust boundary and domain validation in Python.
5. Explicit timeout/cancellation semantics where applicable.
6. A clear read-only versus mutating classification.
7. A test proving the command calls the intended existing service.
8. A test proving invalid input and backend failure are handled without false success.

Mutating commands must additionally define confirmation requirements, authorization source, rollback/recovery behaviour and audit/history behaviour.

Do not rename or remove existing JSON-RPC methods without a compatibility period. Prefer adapters that preserve existing Python method contracts. Add versioning or capability negotiation if the bridge and sidecar can be updated independently.

## 4. Required testing strategy

### A. Baseline before migration
- Run the complete existing Python suite on Windows with the supported Python versions.
- Save the exact commit SHA, commands, test counts and failures.
- Run packaging smoke tests and sidecar lifecycle tests.
- Record existing known failures separately; do not silently count pre-existing failures as migration regressions.

### B. Python regression suite
Run all existing tests, including (not limited to):
- storage scanning, file metadata/signature, duplicate detection, duplicate hard-links and review
- cleanup policy and cleanup manager
- directory browser
- process discovery, streaming, identity verification, authorization and graceful closer
- battery adapter
- adaptive policy engine
- startup adapter
- sidecar protocol, adapters, integration, packaging and parent watchdog
- UI/service tests retained for the legacy application during the transition

### C. React tests (required before a screen is considered migrated)
- Component rendering for loading, success, empty, stale, partial and error states.
- User interaction tests for search, filters, sorting, pagination, confirmation and navigation.
- Contract tests for every Tauri command called by the screen.
- Tests that unavailable data is not converted to zero or fabricated defaults.
- Tests that buttons remain disabled/hidden when backend capability or authorization is absent.
- Accessibility checks for labels, keyboard navigation, focus management and status announcements.
- Visual regression/screenshot checks for shared layout and responsive breakpoints where practical.

### D. Rust/Tauri and sidecar tests
- Command input validation and response serialization.
- JSON-RPC request/response framing and malformed messages.
- Sidecar startup, timeout, crash, EOF, shutdown and orphan prevention.
- Allowlist enforcement and least-privilege capability checks.
- Windows-specific process/registry/filesystem behaviour must run on Windows, not be inferred from Linux mocks.

### E. End-to-end Windows acceptance
On a clean Windows 10/11 test machine or VM:
- Install and launch the packaged app.
- Verify each screen against the acceptance checklist above.
- Verify settings/history survive restart and upgrade.
- Exercise storage scans only against disposable test directories.
- Exercise cleanup only against disposable files and confirm Recycle Bin/rollback behaviour.
- Exercise process controls only against a disposable test application, never critical/system processes.
- Verify startup-app changes only against a disposable test entry with restoration.
- Verify sidecar exits on normal close and forced app exit.
- Uninstall and confirm user data follows the documented retention policy.

## 5. Migration order and gates

| Order | Work | Exit gate |
|---|---|---|
| 0 | Capture baseline and freeze backend contracts | Baseline results recorded; no unreviewed backend behaviour changes |
| 1 | Shared React design system, app shell and theme bootstrap | Component tests; saved theme loads before first render |
| 2 | Tauri command/JSON-RPC contract | Contract tests, schema validation, error mapping and sidecar lifecycle pass |
| 3 | Dashboard | Dashboard acceptance checklist passes |
| 4 | Storage | All listed storage parity tests pass; no cleanup safety regression |
| 5 | Process & RAM | Identity and authorization tests pass; v1 scope and disabled action gates preserved |
| 6 | Battery and Applications | Adapter-backed data and unsupported states verified |
| 7 | Startup Apps | Read-only until reversible restore is implemented and tested |
| 8 | Adaptive Control | Preferences clearly separated from active enforcement; safety policy unchanged |
| 9 | Activity History and Settings | Persistence and cross-screen behaviour verified |
| 10 | Packaging and release | Windows installer, upgrade, shutdown and end-to-end checks pass |
| 11 | Retire PySide6 production path | Only after all features pass; legacy code/tests may remain temporarily for rollback |

A screen is **not migrated** just because it renders or compiles. It is migrated only when its acceptance tests pass against the real backend and the required platform validation is complete.

## 6. Current known gaps to track explicitly

These are known from the reviewed React/Tauri implementation and must not be treated as completed functionality:

- Storage UI parity is incomplete where it exposes only disk usage and directory listing; the broader scan, duplicate, review, metadata and cleanup workflows must be restored.
- Process UI is largely read-only; Close/Details actions were disabled. Preserve the safe v1 scope and do not wire a PID-only action shortcut.
- Startup-app enabling/restoration is not implemented; deletion-based disable is not safely reversible.
- Adaptive Control UI currently represents preferences rather than verified live resource enforcement.
- Several Settings options are persisted preferences without the corresponding OS/application side effects.
- Activity History is read-only and may lack pagination/clear-history operations.
- Application metadata fields absent from the backend must remain explicitly unavailable.
- Tailwind class names assembled dynamically may be omitted by the production scanner; use static class maps or an explicit safelist and test the built CSS.
- The Tauri configuration previously used `csp: null`; set and verify a restrictive policy before release.
- Frontend package scripts previously had a build script but no dedicated test script; add a real test runner and make it a required CI job.
- Dashboard polling must be checked for overlapping requests.
- The old PySide6 launcher/installer and new Tauri path must not remain ambiguous at release time.

## 7. Definition of done

The redesign is accepted only when all of the following are true:

- [ ] Every feature in Section 2 is marked **Pass**, **Not applicable with evidence**, or **Known limitation explicitly accepted by the product owner**.
- [ ] No unapproved regression exists in the Python suite.
- [ ] React unit/component/contract tests pass.
- [ ] Rust/Tauri and sidecar tests pass.
- [ ] Windows CI passes for supported Python versions.
- [ ] Windows installer and end-to-end acceptance pass on a real Windows environment.
- [ ] Safety-critical actions are still deny-by-default and identity-bound.
- [ ] Settings, history and user data survive the supported upgrade path.
- [ ] Release notes disclose any accepted limitations.
- [ ] PySide6 is not removed from the production path until the new app passes these gates.

**Release rule:** If a gate fails, stop the migration at that feature. Keep the existing implementation available and fix the gap before retiring it.
