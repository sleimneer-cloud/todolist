from dataclasses import dataclass
from datetime import date


@dataclass
class Task:
    id: int | None
    text: str
    due_date: date | None
    done: bool = False
