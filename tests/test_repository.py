import sqlite3
from datetime import datetime, timedelta

import pytest

from todolist.repository import LocalSqliteRepository


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
