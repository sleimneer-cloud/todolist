from datetime import date

SOON_THRESHOLD_DAYS = 3

TIER_COLORS = {
    "urgent": "#e5484d",
    "soon": "#f5a623",
    "muted": "#8a8f98",
}


def urgency_tier(due_date: date | None, today: date) -> str:
    if due_date is None:
        return "muted"
    days_left = (due_date - today).days
    if days_left <= 0:
        return "urgent"
    if days_left <= SOON_THRESHOLD_DAYS:
        return "soon"
    return "muted"


def urgency_color(due_date: date | None, today: date | None = None) -> str:
    return TIER_COLORS[urgency_tier(due_date, today or date.today())]
