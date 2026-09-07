from dataclasses import dataclass
from datetime import date


@dataclass
class Task:
    id: int | None
    text: str
    due_date: date | None
    start_date: date | None = None
    done: bool = False
