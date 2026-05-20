from fastapi import APIRouter
from app import errors
from app.services import dashboard

router = APIRouter()

@router.get("/summaries/next-payday")
def next_payday_summary(today: str | None = None):
    result = dashboard.get_next_payday_summary(today)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result
