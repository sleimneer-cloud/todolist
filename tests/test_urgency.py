from datetime import date, timedelta

from todolist.urgency import TIER_COLORS, urgency_tier

TODAY = date(2026, 9, 7)


def test_overdue_is_urgent():
    assert urgency_tier(TODAY - timedelta(days=1), TODAY) == "urgent"


def test_due_today_is_urgent():
    assert urgency_tier(TODAY, TODAY) == "urgent"


def test_one_day_out_is_soon():
    assert urgency_tier(TODAY + timedelta(days=1), TODAY) == "soon"


def test_three_days_out_is_soon():
    assert urgency_tier(TODAY + timedelta(days=3), TODAY) == "soon"


def test_four_days_out_is_muted():
    assert urgency_tier(TODAY + timedelta(days=4), TODAY) == "muted"


def test_no_due_date_is_muted():
    assert urgency_tier(None, TODAY) == "muted"


def test_all_tiers_have_a_color():
    assert set(TIER_COLORS) == {"urgent", "soon", "muted"}
