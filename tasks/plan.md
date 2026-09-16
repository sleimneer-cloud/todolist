# Implementation Plan: Desktop Todo Widget

Spec: `../SPEC.md`

## Overview
Python + PySide6 desktop widget, pinned bottom-right and always-on-top, backed by local SQLite
through a `TaskRepository` interface (swappable later for a FastAPI/MariaDB-backed remote
implementation). Build the data layer first, then the highest-risk UI behavior (frameless
always-on-top window positioning) early so platform quirks surface fast, then layer on
interactions and due-date urgency coloring.

## Architecture Decisions
- **Data layer behind an interface from day one.** `TaskRepository` (Protocol) +
  `LocalSqliteRepository` are built in Task 1, before any UI exists, so the UI never talks to
  SQLite directly — keeps the future remote-sync swap a drop-in replacement.
- **`due_date` is part of the schema from Task 1**, even though the UI doesn't expose it until
  Task 4. Adding a column later is a migration; including it now avoids that entirely.
- **Window chrome (frameless / always-on-top / bottom-right position) is built in Task 2, not
  deferred to polish.** It's the part most likely to behave unexpectedly on macOS/Qt, so it's
  tackled right after the data layer instead of at the end — fail fast on the riskiest unknown.
- **Urgency coloring is a pure function (`urgency.py`)**, unit-testable independent of any Qt
  widget, so the color-tier boundaries can be verified without launching the UI.

## Task List

### Phase 1: Foundation
- [ ] Task 1: Data layer — model, schema, repository

### Checkpoint: Foundation + Window
- [ ] `pytest` passes for repository tests
- [ ] App launches as a frameless, always-on-top window pinned bottom-right
- [ ] Typing a task and pressing Enter adds it to the visible list and to SQLite
- [ ] Restarting the app shows the same list (persistence confirmed)
- [ ] Review with human before proceeding

### Phase 2: Core Interactions
- [ ] Task 3: Complete / edit / delete a task
- [ ] Task 4: Due dates + urgency coloring

### Checkpoint: Core Features Complete
- [ ] All of: add, complete, edit, delete, due date, color-by-urgency work end-to-end in the UI
- [ ] `pytest` passes (repository + urgency-function tests)
- [ ] Review with human before proceeding

### Phase 3: Polish
- [ ] Task 5: Lock down window behavior + full walkthrough

### Checkpoint: Complete
- [ ] Every Success Criterion in `SPEC.md` verified manually
- [ ] `pytest` passes
- [ ] Ready for review

### Phase 4: Weekly Work Journal
- [ ] Task 6: `created_at` tracking + weekly repository query
- [ ] Task 7: LLM weekly report client
- [ ] Task 8: In-app trigger + report dialog

### Checkpoint: Weekly Journal Complete
- [ ] `pytest` passes (repository week-query tests + report-client tests)
- [ ] Adding a task today, then generating this week's journal, includes that task
- [ ] Generating with no tasks in the current week shows a clear empty-state message, not an error
- [ ] Generating with no API key configured shows a clear setup message, not a crash
- [ ] Review with human before proceeding

---

## Task 1: Data layer — model, schema, repository

**Description:** Build the persistence foundation before any UI exists: the `Task` model, the
SQLite schema (including `due_date` from the start), and the `TaskRepository` interface with its
local SQLite implementation. This is the highest-dependency piece — everything else reads/writes
through it.

**Acceptance criteria:**
- [ ] `Task` dataclass has `id`, `text`, `due_date` (optional), `done` (bool)
- [ ] `LocalSqliteRepository` implements `add`, `update`, `delete`, `list` against a SQLite file
      under the OS-standard user data directory (no hardcoded absolute paths)
- [ ] Repository is usable standalone (no Qt import required) — confirms UI/data separation

**Verification:**
- [ ] Tests pass: `pytest tests/test_repository.py`
- [ ] Manual check: open a Python shell, add/list/update/delete a task through the repository,
      confirm the SQLite file is created and rows persist across a new process

**Dependencies:** None

**Files likely touched:**
- `src/todolist/models.py`
- `src/todolist/db.py`
- `src/todolist/repository.py`
- `tests/test_repository.py`
- `requirements.txt`

**Estimated scope:** Medium (4-5 files)

---

## Task 2: Window skeleton — frameless, always-on-top, bottom-right, basic add/list

**Description:** Stand up the app entrypoint and main window with the window chrome the spec
requires (no OS frame, always-on-top, pinned to the bottom-right corner of the primary screen),
plus the minimum UI to add a task (text only, no due date yet) and see the list populate from
Task 1's repository. This is the riskiest platform-behavior task, so it's tackled right after the
data layer instead of at the end.

**Acceptance criteria:**
- [ ] Window has no title bar/OS frame and stays on top of other applications
- [ ] Window appears pinned at the bottom-right corner of the primary screen on launch
- [ ] A text input + Enter adds a task via the repository and it appears in the list immediately
- [ ] Restarting the app re-populates the list from SQLite

**Verification:**
- [ ] Tests pass: `pytest` (existing suite still green)
- [ ] Manual check: `python -m todolist.main` — confirm frameless/always-on-top/position by
      switching to another app and back; add a task, quit, relaunch, confirm it's still listed

**Dependencies:** Task 1

**Files likely touched:**
- `src/todolist/main.py`
- `src/todolist/window.py`
- `src/todolist/task_row.py` (basic read-only row for now)

**Estimated scope:** Medium (3 files)

---

## Task 3: Complete / edit / delete a task

**Description:** Wire up the interactive behavior on each task row: clicking the checkbox toggles
`done` (with strikethrough styling) and persists it; clicking the task text switches it to an
inline-editable field that saves on Enter/focus-out; clicking the `×` button deletes the row and
the underlying repository record.

**Acceptance criteria:**
- [ ] Clicking the checkbox toggles strikethrough and persists `done` via the repository
- [ ] Clicking the task text allows inline editing; the new text persists on confirm
- [ ] Clicking `×` removes the row from the UI and the SQLite row

**Verification:**
- [ ] Tests pass: `pytest` (add repository-level tests if `update`/`delete` gain new call shapes)
- [ ] Manual check: toggle complete, edit text, delete a row; restart app and confirm all three
      changes persisted

**Dependencies:** Task 2

**Files likely touched:**
- `src/todolist/task_row.py`
- `src/todolist/window.py` (signal wiring)

**Estimated scope:** Small (2 files)

---

## Task 4: Due dates + urgency coloring

**Description:** Add an optional due-date field to the add-task form and the inline edit flow.
Implement urgency-tier color logic as a pure, independently testable function, then apply it to
each task row's styling based on its `due_date`.

**Acceptance criteria:**
- [ ] Add-task form and inline edit both accept an optional due date
- [ ] `urgency_color(due_date)` (or equivalent) returns the correct tier for: overdue, due today,
      1-3 days out, 4+ days out, and no due date
- [ ] Task rows visually reflect their tier per `SPEC.md`'s default color rules

**Verification:**
- [ ] Tests pass: `pytest tests/test_urgency.py` covering all five boundary cases above
- [ ] Manual check: create tasks in each urgency tier, confirm the three visual color groups are
      distinguishable at a glance

**Dependencies:** Task 1 (schema already has `due_date`), Task 3 (row widget exists)

**Files likely touched:**
- `src/todolist/urgency.py`
- `tests/test_urgency.py`
- `src/todolist/task_row.py`
- `src/todolist/window.py` (add-task form)

**Estimated scope:** Medium (4 files)

---

## Task 5: Lock down window behavior + full walkthrough

**Description:** Finish the window-chrome requirements not yet covered — disable manual resize
and drag-move, and confirm the bottom-right position recalculates correctly if the screen
geometry differs (e.g. external display) — then run through every Success Criterion in
`SPEC.md` end-to-end as a final gate.

**Acceptance criteria:**
- [ ] Window cannot be resized or dragged by the user
- [ ] Bottom-right position is computed from actual screen geometry, not a hardcoded coordinate
- [ ] Every numbered Success Criterion in `SPEC.md` passes a manual check

**Verification:**
- [ ] Tests pass: full `pytest` suite
- [ ] Manual check: attempt to resize/drag (should have no effect); walk through
      add → complete → edit → delete → due-date-coloring → restart-persistence in one session

**Dependencies:** Task 2, Task 3, Task 4

**Files likely touched:**
- `src/todolist/window.py`

**Estimated scope:** Small (1 file)

---

## Task 6: `created_at` tracking + weekly repository query

**Description:** Add a `created_at` column so every task records when it was registered, and add
a repository method to fetch tasks whose `created_at` falls within a given week. This is the
foundation for the journal feature — everything else (LLM call, UI trigger) reads from this
query, so it goes first, same reasoning as Task 1.

**Decision:** "This week" is anchored on `created_at` (registration date), not `due_date` or a
new `completed_at` — the user wants a record of what they worked on, not what was scheduled.
Week boundaries use the ISO calendar week (Monday-Sunday), via `date.isocalendar()` — no new
dependency needed, stdlib covers it.

**Acceptance criteria:**
- [ ] `tasks` table has a `created_at` column (`TEXT`, ISO datetime), backfilled for existing
      rows with the row's current value or a fixed default (existing rows predate this field —
      exact date is unknowable, so document the backfill choice rather than guessing precision)
- [ ] `LocalSqliteRepository.add()` stamps `created_at` automatically — never a caller-supplied
      value (unlike `due_date`/`start_date`, this is not user-editable)
- [ ] New method `list_for_week(monday: date, sunday: date) -> list[Task]` returns tasks with
      `created_at` in that inclusive range, ordered by `created_at`
- [ ] `TaskRepository` Protocol gains `list_for_week` so the interface stays the single point of
      data access (per `SPEC.md`'s "Always" boundary)

**Verification:**
- [ ] Tests pass: `pytest tests/test_repository.py` — cases: task created inside the week, task
      created before the week, task created after the week (both excluded), empty week
- [ ] Manual check: add a task, confirm it shows up in `list_for_week` for the current week via a
      Python shell

**Dependencies:** Task 1 (repository/schema already exists)

**Files likely touched:**
- `src/todolist/db.py` (migration, mirrors the existing `start_date` `ALTER TABLE` pattern)
- `src/todolist/models.py` (`Task.created_at` field)
- `src/todolist/repository.py`
- `tests/test_repository.py`

**Estimated scope:** Small (4 files)

---

## Task 7: LLM weekly report client

**Description:** A pure module that takes a list of `Task` and a week range, formats them into a
prompt, calls an LLM API, and returns the generated report text (or raises a typed error the UI
layer can catch and show). No Qt imports — testable and runnable standalone, same separation
principle as `TaskRepository`.

**Decision:** Use the Anthropic Claude API directly over stdlib `urllib.request` / `http.client`
rather than adding the `anthropic` SDK as a dependency — one HTTP call doesn't need a client
library, and `SPEC.md`'s boundaries require asking before new dependencies. Store the API key
via macOS Keychain, accessed by shelling out to the built-in `/usr/bin/security` CLI (stdlib
`subprocess`, no new dependency) — falls back to a local config file with owner-only permissions
if `security` is unavailable (non-macOS). **Flag for human review before starting:** confirm
this stdlib-only approach is acceptable instead of `pip install anthropic` + `keyring`, since it
means hand-rolling request signing/error-handling that a SDK would otherwise cover.

**Acceptance criteria:**
- [ ] `generate_weekly_report(tasks: list[Task], week_start: date, week_end: date) -> str`
      builds a prompt from the tasks (text, done/not-done, due date if present) and returns the
      model's response text
- [ ] Raises a specific exception (not a bare `Exception`) for: missing API key, network/API
      error, empty task list (caller decides whether empty is an error or a UI empty-state)
- [ ] API key is read from Keychain/config at call time, never hardcoded or logged
- [ ] No Qt import anywhere in this module

**Verification:**
- [ ] Tests pass: `pytest tests/test_weekly_report.py` — prompt-building logic tested without
      network calls (mock the HTTP call); error paths tested for missing key and API failure
- [ ] Manual check: with a real API key configured, call the function directly in a Python shell
      against a handful of real tasks and confirm the output reads like a work journal

**Dependencies:** Task 6 (needs `Task` objects with `created_at` to build the prompt)

**Files likely touched:**
- `src/todolist/weekly_report.py` (new)
- `tests/test_weekly_report.py` (new)

**Estimated scope:** Medium (2 files, new module)

---

## Task 8: In-app trigger + report dialog

**Description:** Add a way to trigger "generate this week's journal" from the widget (e.g. a
small button or menu item), run the repository query + LLM call on a background thread so the
always-on-top widget never freezes, and show the result in a simple read-only dialog the user
can select/copy text from.

**Acceptance criteria:**
- [ ] A visible control in the widget starts report generation for the current ISO week
- [ ] The UI thread is never blocked — a `QThread`/`QRunnable` (or `QtConcurrent`-style worker)
      does the repository query + LLM call, signaling back to the main thread on completion
- [ ] While generating, the user gets a visible "generating..." state (button disabled or a
      spinner) instead of a frozen-looking widget
- [ ] On success, a `QDialog` shows the generated text, selectable/copyable
- [ ] On failure (no API key, network error, empty week), the same dialog (or a small message)
      shows a clear, specific message — never a silent failure or raw stack trace

**Verification:**
- [ ] Tests pass: full `pytest` suite (this task is UI wiring, no new pure-logic tests expected
      beyond what Tasks 6-7 already cover, consistent with this repo's GUI-is-manual-only
      testing strategy)
- [ ] Manual check: add a couple of tasks this week, click generate, confirm the dialog shows a
      real report; retry with the API key temporarily removed and confirm the error message is
      clear instead of a crash

**Dependencies:** Task 6, Task 7

**Files likely touched:**
- `src/todolist/window.py` (trigger control, worker thread wiring)
- `src/todolist/weekly_report_dialog.py` (new, or inline `QDialog` if small enough)

**Estimated scope:** Medium (2 files)

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| PySide6 frameless/always-on-top window flags behave inconsistently on macOS | High | Tackled in Task 2, right after the data layer, so surprises surface early rather than at the end |
| Due-date/urgency tier boundaries are ambiguous (e.g. what counts as "today") | Medium | Boundaries are pure-function unit tested in Task 4 against explicit cases, not left to visual judgment alone |
| SQLite file location differs across environments | Low | Use Qt's standard user-data-directory API rather than a hardcoded path (Task 1) |
| Hand-rolled HTTP call to the LLM API (Task 7) has to cover retries/error-shapes a SDK would give for free | Medium | Keep the client function small and single-purpose; revisit adding the `anthropic` SDK later if error handling grows past a few cases |
| LLM API call blocking the always-on-top UI thread would freeze a widget meant to always be responsive | High | Task 8 explicitly requires a background-thread worker before any dialog is shown |
| Existing rows have no real `created_at` value to backfill (Task 6) | Low | Documented as a known gap: backfilled rows land in whatever week the migration ran, not their true creation week |

## Open Questions
- Exact hex colors for the three urgency tiers — left to implementation-time choice within
  the "eye-catching / medium / muted" intent from `SPEC.md`; flag for a quick look once Task 4
  is visually running.
- Task 7's stdlib-only HTTP approach vs. adding the `anthropic` SDK dependency — needs a human
  decision before Task 7 starts, since `SPEC.md` requires asking before new dependencies.
- Which Claude model to call, and how to bound response length/cost per generation — not yet
  decided; default to a fast/cheap model unless told otherwise.
- No way yet to generate a *past* week's journal (only "this week") — acceptable for v1, flagged
  as a likely fast-follow rather than in scope now.
