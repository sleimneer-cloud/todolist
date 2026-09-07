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
- [ ] Task 5: Lock down window behavior + full walkthrough
  - Acceptance: window cannot be resized or dragged; bottom-right position computed from real screen geometry; every SPEC.md Success Criterion passes manual check
  - Verify: full `pytest` suite; manual resize/drag attempt (no effect); full add→complete→edit→delete→coloring→restart walkthrough in one session
  - Files: `src/todolist/window.py`
  - Dependencies: Task 2, Task 3, Task 4

## Checkpoint: Complete
- [ ] Every Success Criterion in `SPEC.md` verified manually
- [ ] `pytest` passes
- [ ] Ready for review
