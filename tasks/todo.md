# Todo: Desktop Todo Widget

Plan: `plan.md` · Spec: `../SPEC.md`

## Phase 1: Foundation
- [x] Task 1: Data layer — model, schema, repository
  - Acceptance: `Task` dataclass (id, text, due_date, done); `LocalSqliteRepository` implements add/update/delete/list against SQLite in the OS user-data dir; usable with no Qt import
  - Verify: `pytest tests/test_repository.py`; manual CRUD check via a Python shell across process restarts
  - Files: `src/todolist/models.py`, `src/todolist/db.py`, `src/todolist/repository.py`, `tests/test_repository.py`, `requirements.txt`
  - Dependencies: None

## Checkpoint: Foundation + Window
- [ ] `pytest` passes for repository tests
- [ ] App launches frameless, always-on-top, pinned bottom-right
- [ ] Adding a task via the input updates the visible list and SQLite
- [ ] Restart shows the same list (persistence confirmed)
- [ ] Review with human before proceeding

## Phase 2: Core Interactions
- [x] Task 2: Window skeleton — frameless, always-on-top, bottom-right, basic add/list
  - Acceptance: no OS frame, stays on top, pinned bottom-right on launch; text input + Enter adds a task and it appears immediately; restart re-populates from SQLite
  - Verify: existing `pytest` suite green; manual check of frameless/always-on-top/position, add-then-restart persistence
  - Files: `src/todolist/main.py`, `src/todolist/window.py`, `src/todolist/task_row.py`
  - Dependencies: Task 1

- [x] Task 3: Complete / edit / delete a task
  - Acceptance: checkbox toggles strikethrough + persists `done`; clicking text allows inline edit that persists; `×` deletes row + DB record
  - Verify: `pytest` (add repository tests if call shapes change); manual toggle/edit/delete + restart to confirm persistence
  - Files: `src/todolist/task_row.py`, `src/todolist/window.py`
  - Dependencies: Task 2

- [x] Task 4: Due dates + urgency coloring
  - Acceptance: add/edit forms accept optional due date; `urgency_color(due_date)` correct for overdue, due-today, 1-3 days, 4+ days, no-date; task rows styled per tier
  - Verify: `pytest tests/test_urgency.py` covering all five cases; manual check that the three color tiers are visually distinguishable
  - Files: `src/todolist/urgency.py`, `tests/test_urgency.py`, `src/todolist/task_row.py`, `src/todolist/window.py`
  - Dependencies: Task 1, Task 3

## Checkpoint: Core Features Complete
- [ ] Add, complete, edit, delete, due date, and color-by-urgency all work end-to-end in the UI
- [ ] `pytest` passes (repository + urgency tests)
- [ ] Review with human before proceeding

## Phase 3: Polish
- [x] Task 5: Lock down window behavior + full walkthrough
  - Acceptance: window cannot be resized or dragged; bottom-right position computed from real screen geometry; every SPEC.md Success Criterion passes manual check
  - Verify: full `pytest` suite; manual resize/drag attempt (no effect); full add→complete→edit→delete→coloring→restart walkthrough in one session
  - Files: none — resize/drag lock already fell out of Task 2 (`setFixedSize` pins min==max; no drag handlers were ever written), so nothing to change here
  - Dependencies: Task 2, Task 3, Task 4

## Checkpoint: Complete
- [x] Every Success Criterion in `SPEC.md` verified manually
- [x] `pytest` passes
- [x] Ready for review

## Phase 4: Weekly Work Journal
- [ ] Task 6: `created_at` tracking + weekly repository query
  - Acceptance: `tasks` table has `created_at` (auto-stamped on `add`, not caller-supplied); `list_for_week(monday, sunday)` returns tasks with `created_at` in that inclusive range; `TaskRepository` Protocol gains the method
  - Verify: `pytest tests/test_repository.py` (inside/before/after week, empty week cases); manual add-then-query check via Python shell
  - Files: `src/todolist/db.py`, `src/todolist/models.py`, `src/todolist/repository.py`, `tests/test_repository.py`
  - Dependencies: Task 1

- [ ] Task 7: LLM weekly report client
  - Acceptance: `generate_weekly_report(tasks, week_start, week_end) -> str` builds a prompt and returns model output; raises specific errors for missing API key / network failure; API key read from Keychain (or local config fallback), never hardcoded; no Qt import
  - Verify: `pytest tests/test_weekly_report.py` with the HTTP call mocked (prompt-building + error paths); manual run against a real API key
  - Files: `src/todolist/weekly_report.py`, `tests/test_weekly_report.py`
  - Dependencies: Task 6
  - **Needs a decision before starting:** stdlib-only HTTP call vs. adding the `anthropic` SDK — `SPEC.md` requires asking before new dependencies

- [ ] Task 8: In-app trigger + report dialog
  - Acceptance: a control in the widget starts generation for the current ISO week; repository query + LLM call run off the UI thread; a "generating..." state is visible while running; success shows a copyable `QDialog`; failure (no key / network / empty week) shows a clear message, never a crash or silent failure
  - Verify: full `pytest` suite; manual click-through with tasks present, with an empty week, and with the API key removed
  - Files: `src/todolist/window.py`, `src/todolist/weekly_report_dialog.py`
  - Dependencies: Task 6, Task 7

## Checkpoint: Weekly Journal Complete
- [ ] `pytest` passes (repository week-query tests + report-client tests)
- [ ] Adding a task today, then generating this week's journal, includes that task
- [ ] Generating with no tasks in the current week shows a clear empty-state message, not an error
- [ ] Generating with no API key configured shows a clear setup message, not a crash
- [ ] Review with human before proceeding
