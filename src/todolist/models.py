from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Task:
    id: int | None
    text: str
    due_date: datetime | None
    start_date: date | None = None
    done: bool = False
