from fastapi import APIRouter, HTTPException
from app.services import payments
from app.models import payment_models
from datetime import datetime

router = APIRouter()

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

    return payments.create_payment(data)


@router.post("/payments/weekly")
def weekly_budget(data: payment_models.WeeklyBudgetRequest):
    try:
        payday = datetime.strptime(data.payday, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="payday must be YYYY-MM-DD")
    
    return payments.get_weekly_budget(data.payday)