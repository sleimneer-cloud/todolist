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
**결정됨 (당초 "결정 필요" 항목):** Anthropic API는 비용 때문에 제외 — 무료 티어가 있는 Groq를
OpenAI 호환 Chat Completions API로 stdlib `urllib`만으로 직접 호출 (SDK 추가 없음). 모델은
`GROQ_MODEL` 환경변수로 설정 가능, 기본값 `llama-3.3-70b-versatile`. API 키는 Keychain이 아니라
`GROQ_API_KEY` 환경변수로 보관 (SPEC.md의 "자격 증명 커밋 금지" 원칙에 맞으면서 가장 단순한 방식).

- [x] Task 6: `created_at` tracking + weekly repository query
  - Acceptance: `tasks` table has `created_at` (auto-stamped on `add`, not caller-supplied); `list_for_week(monday, sunday)` returns tasks with `created_at` in that inclusive range; `TaskRepository` Protocol gains the method
  - Verify: `pytest tests/test_repository.py` (inside/before/after week, empty week, legacy-NULL cases) — all passing
  - Files: `src/todolist/db.py`, `src/todolist/models.py`, `src/todolist/repository.py`, `tests/test_repository.py`

- [x] Task 7: LLM weekly report client
  - Acceptance: `generate_weekly_report(tasks, week_start, week_end) -> str` builds a prompt and returns model output; raises `MissingApiKeyError`/`WeeklyReportError` for missing key / network / API / malformed-response failures; API key read from `GROQ_API_KEY` env var, never hardcoded; no Qt import
  - Verify: `pytest tests/test_weekly_report.py` with `urllib.request.urlopen` mocked (prompt-building + every error path) — all passing
  - Files: `src/todolist/weekly_report.py`, `tests/test_weekly_report.py`

- [x] Task 8: In-app trigger + report dialog
  - Acceptance: 📄 header button starts generation for the current ISO week (Mon–Sun); repository query + LLM call run on a `QThread` off the UI thread; button shows ⏳ and disables while running; success opens a copyable `WeeklyReportDialog` (read-only `QTextEdit` + 복사 버튼); failure shows `QMessageBox.critical`; an empty week short-circuits to `QMessageBox.information` before any network call
  - Verify: full `pytest` suite green; headless functional check driving `_on_generate_report()` end-to-end with `GROQ_API_KEY` unset, confirming the failed-signal message and button reset
  - Files: `src/todolist/window.py`, `src/todolist/weekly_report_dialog.py`, `src/todolist/ui/main_window.ui`

## Checkpoint: Weekly Journal Complete
- [x] `pytest` passes (repository week-query tests + report-client tests) — 44/44
- [x] Adding a task today, then generating this week's journal, includes that task (list_for_week 테스트로 확인)
- [x] Generating with no tasks in the current week shows a clear empty-state message, not an error
- [x] Generating with no API key configured shows a clear setup message, not a crash
- [ ] Review with human before proceeding
