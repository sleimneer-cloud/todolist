from datetime import date, datetime
from pathlib import Path
from typing import Protocol

from todolist.db import DEFAULT_DB_PATH, connect
from todolist.models import Task

_UNSET = object()


class TaskRepository(Protocol):
    def add(
        self, text: str, due_date: datetime | None, start_date: date | None = None
    ) -> Task: ...
    def update(
        self,
        task_id: int,
        *,
        text: str | None = _UNSET,
        due_date: datetime | None = _UNSET,
        start_date: date | None = _UNSET,
        done: bool | None = _UNSET,
    ) -> Task: ...
    def delete(self, task_id: int) -> None: ...
    def list(self) -> list[Task]: ...
    def list_for_week(self, start: date, end: date) -> list[Task]: ...


def _row_to_task(row: tuple) -> Task:
    task_id, text, due_date_str, start_date_str, done, created_at_str = row
    return Task(
        id=task_id,
        text=text,
        due_date=datetime.fromisoformat(due_date_str) if due_date_str else None,
        start_date=date.fromisoformat(start_date_str) if start_date_str else None,
        done=bool(done),
        created_at=datetime.fromisoformat(created_at_str) if created_at_str else None,
    )


class LocalSqliteRepository:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self._conn = connect(db_path)

    def add(
        self, text: str, due_date: datetime | None, start_date: date | None = None
    ) -> Task:
        created_at = datetime.now()
        cursor = self._conn.execute(
            "INSERT INTO tasks (text, due_date, start_date, done, created_at) "
            "VALUES (?, ?, ?, 0, ?)",
            (
                text,
                due_date.isoformat() if due_date else None,
                start_date.isoformat() if start_date else None,
                created_at.isoformat(),
            ),
        )
        self._conn.commit()
        return Task(
            id=cursor.lastrowid,
            text=text,
            due_date=due_date,
            start_date=start_date,
            done=False,
            created_at=created_at,
        )

    def update(
        self,
        task_id: int,
        *,
        text: str | None = _UNSET,
        due_date: datetime | None = _UNSET,
        start_date: date | None = _UNSET,
        done: bool | None = _UNSET,
    ) -> Task:
        current = self._get(task_id)
        new_text = current.text if text is _UNSET else text
        new_due_date = current.due_date if due_date is _UNSET else due_date
        new_start_date = current.start_date if start_date is _UNSET else start_date
        new_done = current.done if done is _UNSET else done
        self._conn.execute(
            "UPDATE tasks SET text = ?, due_date = ?, start_date = ?, done = ? WHERE id = ?",
            (
                new_text,
                new_due_date.isoformat() if new_due_date else None,
                new_start_date.isoformat() if new_start_date else None,
                int(new_done),
                task_id,
            ),
        )
        self._conn.commit()
        return Task(
            id=task_id,
            text=new_text,
            due_date=new_due_date,
            start_date=new_start_date,
            done=new_done,
            created_at=current.created_at,
        )

    def delete(self, task_id: int) -> None:
        self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._conn.commit()

    def list(self) -> list[Task]:
        rows = self._conn.execute(
            "SELECT id, text, due_date, start_date, done, created_at FROM tasks ORDER BY id"
        ).fetchall()
        return [_row_to_task(row) for row in rows]

    def list_for_week(self, start: date, end: date) -> list[Task]:
        # 파라미터 이름은 반드시 월~일일 필요는 없다 — 호출자가 임의의 7일(또는
        # 다른 길이) 구간을 넘겨도 그대로 동작한다 (window.py는 "오늘부터
        # 거꾸로 6일"을 넘긴다). created_at은
        # "YYYY-MM-DDTHH:MM:SS.ffffff" ISO 형식 문자열로 저장돼 있다. SQLite의
        # date()는 이 T-구분자 형식을 그대로 인식하므로
        # (sqlite.org/lang_datefunc.html) 별도 변환 없이 날짜만 뽑아 비교한다.
        rows = self._conn.execute(
            "SELECT id, text, due_date, start_date, done, created_at FROM tasks "
            "WHERE date(created_at) BETWEEN ? AND ? ORDER BY id",
            (start.isoformat(), end.isoformat()),
        ).fetchall()
        return [_row_to_task(row) for row in rows]

    def _get(self, task_id: int) -> Task:
        row = self._conn.execute(
            "SELECT id, text, due_date, start_date, done, created_at FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return _row_to_task(row)
