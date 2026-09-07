from datetime import date
from pathlib import Path
from typing import Protocol

from todolist.db import DEFAULT_DB_PATH, connect
from todolist.models import Task


class TaskRepository(Protocol):
    def add(self, text: str, due_date: date | None) -> Task: ...
    def update(
        self,
        task_id: int,
        *,
        text: str | None = None,
        due_date: date | None = None,
        done: bool | None = None,
    ) -> Task: ...
    def delete(self, task_id: int) -> None: ...
    def list(self) -> list[Task]: ...


def _row_to_task(row: tuple) -> Task:
    task_id, text, due_date_str, done = row
    return Task(
        id=task_id,
        text=text,
        due_date=date.fromisoformat(due_date_str) if due_date_str else None,
        done=bool(done),
    )


class LocalSqliteRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self._conn = connect(db_path)

    def add(self, text: str, due_date: date | None) -> Task:
        cursor = self._conn.execute(
            "INSERT INTO tasks (text, due_date, done) VALUES (?, ?, 0)",
            (text, due_date.isoformat() if due_date else None),
        )
        self._conn.commit()
        return Task(id=cursor.lastrowid, text=text, due_date=due_date, done=False)

    def update(
        self,
        task_id: int,
        *,
        text: str | None = None,
        due_date: date | None = None,
        done: bool | None = None,
    ) -> Task:
        current = self._get(task_id)
        new_text = current.text if text is None else text
        new_due_date = current.due_date if due_date is None else due_date
        new_done = current.done if done is None else done
        self._conn.execute(
            "UPDATE tasks SET text = ?, due_date = ?, done = ? WHERE id = ?",
            (
                new_text,
                new_due_date.isoformat() if new_due_date else None,
                int(new_done),
                task_id,
            ),
        )
        self._conn.commit()
        return Task(id=task_id, text=new_text, due_date=new_due_date, done=new_done)

    def delete(self, task_id: int) -> None:
        self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._conn.commit()

    def list(self) -> list[Task]:
        rows = self._conn.execute(
            "SELECT id, text, due_date, done FROM tasks ORDER BY id"
        ).fetchall()
        return [_row_to_task(row) for row in rows]

    def _get(self, task_id: int) -> Task:
        row = self._conn.execute(
            "SELECT id, text, due_date, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return _row_to_task(row)
