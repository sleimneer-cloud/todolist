from datetime import datetime

import pytest

from todolist.due_format import format_due

NOW = datetime(2026, 9, 15, 10, 0)


@pytest.mark.parametrize(
    ("due", "expected"),
    [
        (None, "—"),
        (datetime(2026, 9, 15, 12, 30), "오늘 12:30"),
        (datetime(2026, 9, 15, 0, 0), "오늘 00:00"),
        (datetime(2026, 9, 16, 18, 0), "내일 18:00"),
        (datetime(2026, 9, 14, 23, 59), "1일 지남"),
        (datetime(2026, 9, 10, 9, 0), "5일 지남"),
        (datetime(2026, 9, 17, 9, 0), "2일 뒤"),
        (datetime(2026, 9, 22, 9, 0), "7일 뒤"),
        (datetime(2026, 9, 23, 9, 0), "09-23"),
    ],
)
def test_format_due(due, expected):
    assert format_due(due, NOW) == expected


def test_time_of_day_does_not_shift_the_day_bucket():
    """마감 시각이 이미 지났어도 날짜가 오늘이면 '오늘'이다 (urgency.py와 같은 기준)."""
    assert format_due(datetime(2026, 9, 15, 9, 0), NOW) == "오늘 09:00"
