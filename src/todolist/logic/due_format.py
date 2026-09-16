from datetime import date, datetime

NO_DUE_TEXT = "—"
NEAR_FUTURE_DAYS = 7


def format_due(due: datetime | None, now: datetime | None = None) -> str:
    """마감일시를 목록에 표시할 짧은 상대 표기로 바꾼다.

    긴급도 색상(`urgency.py`)과 같은 기준으로 날짜 단위 비교를 한다. 시각은
    오늘/내일일 때만 덧붙인다 — 그때만 "몇 시까지"가 행동을 바꾸기 때문이다.
    """
    if due is None:
        return NO_DUE_TEXT

    today = (now or datetime.now()).date()
    days_left = (due.date() - today).days

    if days_left == 0:
        return f"오늘 {due:%H:%M}"
    if days_left == 1:
        return f"내일 {due:%H:%M}"
    if days_left < 0:
        return f"{-days_left}일 지남"
    if days_left <= NEAR_FUTURE_DAYS:
        return f"{days_left}일 뒤"
    return f"{due:%m-%d}"


def format_start(start: date | None) -> str:
    return NO_DUE_TEXT if start is None else f"{start:%m-%d} 시작"
