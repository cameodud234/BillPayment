from datetime import datetime, timedelta, date
from app.services import payments, accounts
from app.config import BIWEEKLY_PAYDAY_ANCHOR


def get_next_friday(today: date) -> date:
    days_ahead = 4 - today.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def is_wife_payday(check_date: date) -> bool:
    return (check_date - BIWEEKLY_PAYDAY_ANCHOR).days % 14 == 0


def get_next_payday_summary(today_str: str | None = None):
    try:
        if today_str:
            current_day = datetime.strptime(today_str, "%Y-%m-%d").date()
        else:
            current_day = date.today()

        next_friday = get_next_friday(current_day)
        wife_paid = is_wife_payday(next_friday)

        due_items = payments.get_payments_due_between(current_day, next_friday)
        if isinstance(due_items, dict) and due_items.get("status") == "error":
            return due_items

        total_due = sum(item["amount"] for item in due_items)

        total_balance = accounts.get_total_balance()
        if isinstance(total_balance, dict) and total_balance.get("status") == "error":
            return total_balance

        return {
            "status": "ok",
            "today": str(current_day),
            "next_payday": str(next_friday),
            "your_payday": True,
            "wife_payday": wife_paid,
            "paycheck_count": 2 if wife_paid else 1,
            "total_due": total_due,
            "total_balance": total_balance,
            "remaining_after_bills": total_balance - total_due,
            "payments": due_items
        }

    except ValueError:
        return {
            "status": "error",
            "message": "today must be YYYY-MM-DD"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to build next payday summary: {str(e)}"
        }