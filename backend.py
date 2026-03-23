from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tinydb import TinyDB
from datetime import datetime, timedelta, date

app = FastAPI()

db = TinyDB("bills.json")
payments_table = db.table("payments")


class AddPaymentRequest(BaseModel):
    name: str
    amount: float
    due_date: str
    category: str = ""


class WeeklyBudgetRequest(BaseModel):
    payday: str


@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/payments")
def get_payments():
    rows = payments_table.all()
    rows.sort(key=lambda x: x.get("due_date", ""))

    result = []
    for row in rows:
        result.append({
            "doc_id": row.doc_id,
            "name": row.get("name", ""),
            "amount": row.get("amount", 0.0),
            "due_date": row.get("due_date", ""),
            "category": row.get("category", "")
        })

    return result


@app.post("/add")
def add_payment(data: AddPaymentRequest):
    try:
        datetime.strptime(data.due_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="due_date must be YYYY-MM-DD")

    doc_id = payments_table.insert({
        "name": data.name,
        "amount": data.amount,
        "due_date": data.due_date,
        "category": data.category
    })

    return {"status": "ok", "doc_id": doc_id}


@app.post("/weekly")
def weekly_budget(data: WeeklyBudgetRequest):
    try:
        payday = datetime.strptime(data.payday, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="payday must be YYYY-MM-DD")

    end = payday + timedelta(days=6)

    rows = payments_table.all()
    filtered = []

    for row in rows:
        try:
            due = datetime.strptime(row["due_date"], "%Y-%m-%d").date()
        except Exception:
            continue

        if payday <= due <= end:
            filtered.append({
                "doc_id": row.doc_id,
                "name": row.get("name", ""),
                "amount": row.get("amount", 0.0),
                "due_date": row.get("due_date", ""),
                "category": row.get("category", "")
            })

    total = sum(item["amount"] for item in filtered)

    return {
        "total": total,
        "payments": filtered
    }


# -----------------------------
# NEW PAYDAY SUMMARY ENDPOINT
# -----------------------------

# Put in a known Friday that was one of your wife's paydays.
# Change this to the real anchor date.
WIFE_PAYDAY_ANCHOR = date(2026, 3, 20)


def get_next_friday(today: date) -> date:
    days_ahead = 4 - today.weekday()  # Friday = 4
    if days_ahead < 0:
        days_ahead += 7
    elif days_ahead == 0:
        # If today is Friday, treat today as the payday
        days_ahead = 0
    return today + timedelta(days=days_ahead)


def is_wife_payday(check_date: date) -> bool:
    delta_days = (check_date - WIFE_PAYDAY_ANCHOR).days
    return delta_days % 14 == 0


@app.get("/next-payday-summary")
def next_payday_summary(today: str | None = None):
    """
    Optional query param:
    /next-payday-summary?today=2026-03-22

    If omitted, uses the machine's current local date.
    """
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

        # Bills due from today through next Friday inclusive
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