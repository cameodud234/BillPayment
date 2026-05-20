from datetime import date

from app.services import dashboard
from helpers import assert_service_error


def test_get_next_friday_returns_today_when_today_is_friday():
    assert dashboard.get_next_friday(date(2026, 5, 15)) == date(2026, 5, 15)


def test_get_next_friday_returns_upcoming_friday():
    assert dashboard.get_next_friday(date(2026, 5, 14)) == date(2026, 5, 15)


def test_next_payday_summary_returns_ok_payload(test_db):
    result = dashboard.get_next_payday_summary("2026-05-14")

    assert result["status"] == "ok"
    assert result["today"] == "2026-05-14"
    assert result["next_payday"] == "2026-05-15"
    assert result["paycheck_count"] == 2
    assert result["total_due"] == 0
    assert result["total_balance"] == 0
    assert result["remaining_after_bills"] == 0
    assert result["payments"] == []


def test_next_payday_summary_invalid_date_returns_structured_error(test_db):
    result = dashboard.get_next_payday_summary("05/14/2026")

    assert_service_error(result, "INVALID_DATE_FORMAT", status_code=400)
