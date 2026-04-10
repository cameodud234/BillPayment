from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.services import payments
from app.models import payment_models
from app.domain.payment import PaymentData, WeeklyBudgetData

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

    if data.due_day is not None and not (1 <= data.due_day <= 31):
        raise HTTPException(status_code=400, detail="due_day must be between 1 and 31")

    try:
        payment = PaymentData(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return payments.create_payment(payment)


@router.post("/payments/weekly")
def weekly_budget(data: payment_models.WeeklyBudgetRequest):
    try:
        datetime.strptime(data.payday, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="payday must be YYYY-MM-DD")

    budget = WeeklyBudgetData(**data.model_dump())
    return payments.get_weekly_budget(budget)