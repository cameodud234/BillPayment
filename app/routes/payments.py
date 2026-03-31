from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tinydb import TinyDB
from app.config import DB_PATH
from datetime import datetime, timedelta

router = APIRouter()

db = TinyDB(DB_PATH)
payments_table = db.table("payments")


class AddPaymentRequest(BaseModel):
    name: str
    amount: float
    due_date: str
    category: str = ""


class WeeklyBudgetRequest(BaseModel):
    payday: str


@router.get("/payments")
def get_payments():
    rows = payments_table.all()
    rows.sort(key=lambda x: x.get("due_date", ""))

    return [
        {
            "doc_id": row.doc_id,
            "name": row.get("name", ""),
            "amount": row.get("amount", 0.0),
            "due_date": row.get("due_date", ""),
            "category": row.get("category", "")
        }
        for row in rows
    ]


@router.post("/payments")
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


@router.post("/payments/weekly")
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