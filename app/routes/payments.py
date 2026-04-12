from datetime import datetime
from fastapi import APIRouter, HTTPException

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

    try:
        payment = PaymentData(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = payments.create_payment(payment)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return result


@router.post("/payments/weekly")
def weekly_budget(data: payment_models.WeeklyBudgetRequest):
    try:
        datetime.strptime(data.payday, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="payday must be YYYY-MM-DD")

    budget = WeeklyBudgetData(**data.model_dump())
    return payments.get_weekly_budget(budget)