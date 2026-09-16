import sqlite3
from datetime import date, datetime, timedelta

import pytest

from todolist.data.repository import LocalSqliteRepository


@pytest.fixture
def repo(tmp_path):
    return LocalSqliteRepository(db_path=tmp_path / "todolist.db")


def test_add_returns_task_with_id(repo):
    task = repo.add("buy milk", due_date=None)
    assert task.id is not None
    assert task.text == "buy milk"
    assert task.due_date is None
    assert task.done is False


def test_add_with_due_date(repo):
    due = datetime.now().replace(microsecond=0) + timedelta(days=1)
    task = repo.add("submit report", due_date=due)
    assert task.due_date == due


def test_list_returns_added_tasks(repo):
    repo.add("first", due_date=None)
    repo.add("second", due_date=None)
    tasks = repo.list()
    assert [t.text for t in tasks] == ["first", "second"]


def test_update_text(repo):
    task = repo.add("origianl", due_date=None)
    updated = repo.update(task.id, text="original")
    assert updated.text == "original"
    assert repo.list()[0].text == "original"


def test_update_done(repo):
    task = repo.add("finish task", due_date=None)
    updated = repo.update(task.id, done=True)
    assert updated.done is True
    assert repo.list()[0].done is True


def test_update_due_date(repo):
    task = repo.add("plan trip", due_date=None)
    due = datetime.now().replace(microsecond=0)
    updated = repo.update(task.id, due_date=due)
    assert updated.due_date == due


def test_update_can_clear_due_date(repo):
    task = repo.add("plan trip", due_date=datetime.now().replace(microsecond=0))
    updated = repo.update(task.id, due_date=None)
    assert updated.due_date is None
    assert repo.list()[0].due_date is None


def test_update_text_leaves_due_date_untouched_when_omitted(repo):
    due = datetime.now().replace(microsecond=0)
    task = repo.add("plan trip", due_date=due)
    updated = repo.update(task.id, text="plan the trip")
    assert updated.due_date == due


def test_due_date_preserves_time_component(repo):
    due = datetime(2026, 9, 10, 18, 30)
    task = repo.add("submit report", due_date=due)
    assert task.due_date == due
    assert repo.list()[0].due_date == due


def test_reads_legacy_date_only_due_date(tmp_path):
    db_path = tmp_path / "todolist.db"
    LocalSqliteRepository(db_path=db_path)  # creates schema

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO tasks (text, due_date, start_date, done) VALUES (?, ?, ?, 0)",
            ("legacy task", "2026-09-08", None),
        )

    reopened = LocalSqliteRepository(db_path=db_path)
    assert reopened.list()[0].due_date == datetime(2026, 9, 8)


def test_delete_removes_task(repo):
    task = repo.add("temporary", due_date=None)
    repo.delete(task.id)
    assert repo.list() == []


def test_persists_across_instances(tmp_path):
    db_path = tmp_path / "todolist.db"
    LocalSqliteRepository(db_path=db_path).add("persisted task", due_date=None)

    reopened = LocalSqliteRepository(db_path=db_path)
    assert [t.text for t in reopened.list()] == ["persisted task"]


def test_default_db_path_has_no_qt_dependency():
    import sys

    assert "PySide6" not in sys.modules


def test_add_stamps_created_at_automatically(repo):
    before = datetime.now()
    task = repo.add("stamped", due_date=None)
    after = datetime.now()
    assert task.created_at is not None
    assert before <= task.created_at <= after


def test_list_for_week_includes_only_tasks_created_in_range(tmp_path):
    db_path = tmp_path / "todolist.db"
    LocalSqliteRepository(db_path=db_path)  # creates schema
    monday = date(2026, 9, 14)
    sunday = date(2026, 9, 20)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO tasks (text, done, created_at) VALUES (?, 0, ?)",
            ("before week", "2026-09-13T23:59:00"),
        )
        conn.execute(
            "INSERT INTO tasks (text, done, created_at) VALUES (?, 0, ?)",
            ("monday", "2026-09-14T00:00:00"),
        )
        conn.execute(
            "INSERT INTO tasks (text, done, created_at) VALUES (?, 0, ?)",
            ("sunday", "2026-09-20T23:00:00"),
        )
        conn.execute(
            "INSERT INTO tasks (text, done, created_at) VALUES (?, 0, ?)",
            ("after week", "2026-09-21T00:01:00"),
        )

    reopened = LocalSqliteRepository(db_path=db_path)
    week_tasks = reopened.list_for_week(monday, sunday)
    assert [t.text for t in week_tasks] == ["monday", "sunday"]


def test_completing_a_task_keeps_it_in_the_db_marked_done(repo):
    # 체크박스로 완료 처리해도 delete()가 아니라 update(done=True)만 호출된다
    # (task_row.py) — 그래야 완료한 일도 주간 리포트에 남는다. 여기선
    # repository 계약만 확인한다: done=True로 update해도 행이 사라지지 않는다.
    task = repo.add("완료할 일", due_date=None)
    repo.update(task.id, done=True)
    tasks = repo.list()
    assert len(tasks) == 1
    assert tasks[0].done is True


def test_list_for_week_includes_completed_tasks(repo):
    task = repo.add("이번 주에 끝낸 일", due_date=None)
    repo.update(task.id, done=True)
    today = date.today()
    week_tasks = repo.list_for_week(today, today)
    assert [t.text for t in week_tasks] == ["이번 주에 끝낸 일"]
    assert week_tasks[0].done is True


def test_list_for_week_empty_when_no_tasks_in_range(repo):
    assert repo.list_for_week(date(2020, 1, 6), date(2020, 1, 12)) == []


def test_list_for_week_excludes_legacy_rows_with_no_created_at(tmp_path):
    db_path = tmp_path / "todolist.db"
    LocalSqliteRepository(db_path=db_path)  # creates schema

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO tasks (text, due_date, start_date, done) VALUES (?, ?, ?, 0)",
            ("legacy task", None, None),
        )

    reopened = LocalSqliteRepository(db_path=db_path)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    assert reopened.list_for_week(week_start, week_end) == []
