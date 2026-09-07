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

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| PySide6 frameless/always-on-top window flags behave inconsistently on macOS | High | Tackled in Task 2, right after the data layer, so surprises surface early rather than at the end |
| Due-date/urgency tier boundaries are ambiguous (e.g. what counts as "today") | Medium | Boundaries are pure-function unit tested in Task 4 against explicit cases, not left to visual judgment alone |
| SQLite file location differs across environments | Low | Use Qt's standard user-data-directory API rather than a hardcoded path (Task 1) |

## Open Questions
- Exact hex colors for the three urgency tiers — left to implementation-time choice within
  the "eye-catching / medium / muted" intent from `SPEC.md`; flag for a quick look once Task 4
  is visually running.
