from fastapi import FastAPI
from tinydb import TinyDB
from datetime import datetime, timedelta

app = FastAPI()

db = TinyDB("bills.json")
payments = db.table("payments")


@app.get("/payments")
def get_payments():
    rows = payments.all()
    rows.sort(key=lambda x: x.get("due_date", ""))
    return rows


@app.post("/add")
def add_payment(data: dict):
    payments.insert(data)
    return {"status": "ok"}


@app.post("/weekly")
def weekly(data: dict):
    payday = datetime.strptime(data["payday"], "%Y-%m-%d").date()
    end = payday + timedelta(days=6)

    rows = payments.all()

    filtered = []
    for r in rows:
        due = datetime.strptime(r["due_date"], "%Y-%m-%d").date()
        if payday <= due <= end:
            filtered.append(r)

    total = sum(r["amount"] for r in filtered)

    return {
        "total": total,
        "payments": filtered
    }