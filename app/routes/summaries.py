from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tinydb import TinyDB
from datetime import datetime, timedelta, date
from app.config import DB_PATH

router = APIRouter()
db = TinyDB(DB_PATH)
payments_table = db.table("payments")

# -----------------------------
# PAYDAY SUMMARY
# -----------------------------

WIFE_PAYDAY_ANCHOR = date(2026, 3, 20)

def get_next_friday(today: date) -> date:
    days_ahead = 4 - today.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)

def is_wife_payday(check_date: date) -> bool:
    delta_days = (check_date - WIFE_PAYDAY_ANCHOR).days
    return delta_days % 14 == 0

@router.get("/summaries/next-payday")
def next_payday_summary(today: str | None = None):
    if today:
        try:
            current_day = datetime.strptime(today, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="today must be YYYY-MM-DD")
    else:
        current_day = date.today()

    next_friday = get_next_friday(current_day)
    wife_paid = is_wife_payday(next_friday)

    rows = payments_table.all()
    due_items = []

    for row in rows:
        try:
            due = datetime.strptime(row["due_date"], "%Y-%m-%d").date()
        except Exception:
            continue

        if current_day <= due <= next_friday:
            due_items.append({
                "doc_id": row.doc_id,
                "name": row.get("name", ""),
                "amount": row.get("amount", 0.0),
                "due_date": row.get("due_date", ""),
                "category": row.get("category", "")
            })

    due_items.sort(key=lambda x: x["due_date"])
    total_due = sum(item["amount"] for item in due_items)

    return {
        "today": str(current_day),
        "next_payday": str(next_friday),
        "your_payday": True,
        "wife_payday": wife_paid,
        "paycheck_count": 2 if wife_paid else 1,
        "total_due": total_due,
        "payments": due_items
    }