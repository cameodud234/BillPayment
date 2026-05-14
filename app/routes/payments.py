from datetime import datetime
from fastapi import APIRouter

from app.services import payments, payment_allocations
from app.models import payment_models
from app.domain.payment import PaymentData, WeeklyBudgetData
from app import errors

router = APIRouter()


@router.get("/payments")
def get_payments():
    return payments.get_all_payments()


@router.get("/payments/{payment_id}")
def get_payment(payment_id: int):
    payment = payments.get_payment_by_id(payment_id)

    if payment is None:
        errors.raise_http_error(errors.PAYMENT_NOT_FOUND)

    return payment


@router.get("/payments/{payment_id}/allocations")
def get_payment_allocations(payment_id: int):
    result = payment_allocations.get_payment_allocations(payment_id)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result


@router.post("/payments")
def add_payment(data: payment_models.AddPaymentRequest):
    try:
        datetime.strptime(data.due_date, "%Y-%m-%d")
    except ValueError:
        errors.raise_http_error(errors.VALIDATION_ERROR, "due_date must be YYYY-MM-DD")

    try:
        payment = PaymentData(**data.model_dump())
    except ValueError as e:
        errors.raise_http_error(errors.VALIDATION_ERROR, str(e))

    result = payments.create_payment(payment)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result


@router.put("/payments/{payment_id}")
def update_payment(payment_id: int, data: payment_models.AddPaymentRequest):
    try:
        datetime.strptime(data.due_date, "%Y-%m-%d")
    except ValueError:
        errors.raise_http_error(errors.VALIDATION_ERROR, "due_date must be YYYY-MM-DD")

    try:
        payment = PaymentData(**data.model_dump())
    except ValueError as e:
        errors.raise_http_error(errors.VALIDATION_ERROR, str(e))

    result = payments.update_payment(payment_id, payment)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result


@router.delete("/payments/{payment_id}")
def delete_payment(payment_id: int):
    result = payments.delete_payment(payment_id)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result


@router.post("/payments/weekly")
def weekly_budget(data: payment_models.WeeklyBudgetRequest):
    try:
        datetime.strptime(data.payday, "%Y-%m-%d")
    except ValueError:
        errors.raise_http_error(errors.VALIDATION_ERROR, "payday must be YYYY-MM-DD")

    budget = WeeklyBudgetData(**data.model_dump())
    return payments.get_weekly_budget(budget)
