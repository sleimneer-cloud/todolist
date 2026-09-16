from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Task:
    id: int | None
    text: str
    due_date: datetime | None
    start_date: date | None = None
    done: bool = False
    # 서버(repository)가 add() 시점에 자동으로 찍는다 — 호출자가 넘기지 않는다.
    # 마이그레이션 전에 만들어진 행은 알 방법이 없어 None으로 남는다.
    created_at: datetime | None = None
