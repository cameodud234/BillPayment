from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import payments
from app.models import payment_models
from datetime import datetime, timedelta

router = APIRouter()

class WeeklyBudgetRequest(BaseModel):
    payday: str

@router.get("/payments")
def get_payments():
    return payments.get_all_payments()

@router.post("/payments")
def add_payment(data: payment_models.AddPaymentRequest):
    try:
        datetime.strptime(data.due_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="due_date must be YYYY-MM-DD")
    
    if data.is_recurring not in (0, 1):
        raise HTTPException(status_code=400, detail="is_recurring must be 0 or 1")

    if data.due_day is not None and not (1 <= data.due_day <= 31):
        raise HTTPException(status_code=400, detail="due_day must be between 1 and 31")

    result = payments.create_payment(
        name=data.name,
        amount=data.amount,
        due_date=data.due_date,
        category=data.category,
        account_id=data.account_id,
        is_recurring=data.is_recurring,
        due_day=data.due_day
    )

    return result


@router.post("/payments/weekly")
def weekly_budget(data: WeeklyBudgetRequest):
    try:
        payday = datetime.strptime(data.payday, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="payday must be YYYY-MM-DD")
    
    return payments.get_weekly_budget(data.payday)