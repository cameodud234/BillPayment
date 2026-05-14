from dataclasses import dataclass


@dataclass(frozen=True)
class AppError:
    code: str
    message: str
    status_code: int

def error_response(app_error: AppError, message: str | None = None):
    return {
        "status": "error",
        "error": {
            "code": app_error.code,
            "message": message or app_error.message,
            "status_code": app_error.status_code,
        }
    }

def raise_http_error(app_error: AppError, message: str | None = None):
    from fastapi import HTTPException
    raise HTTPException(
        status_code=app_error.status_code,
        detail={
            "code": app_error.code,
            "message": message or app_error.message
        }
    )

PERSON_NOT_FOUND = AppError(
    code="PERSON_NOT_FOUND",
    message="Person not found",
    status_code=404,
)

ACCOUNT_NOT_FOUND = AppError(
    code="ACCOUNT_NOT_FOUND",
    message="Account not found",
    status_code=404,
)

PAYMENT_NOT_FOUND = AppError(
    code="PAYMENT_NOT_FOUND",
    message="Payment not found",
    status_code=404,
)

PAYMENTS_NOT_FOUND = AppError(
    code="PAYMENT_NOT_FOUND",
    message="Payments not found",
    status_code=404,
)

PERSON_ACCOUNT_EXISTS = AppError(
    code="PERSON_ACCOUNT_EXISTS",
    message="This person already has an account",
    status_code=409,
)

VALIDATION_ERROR = AppError(
    code="VALIDATION_ERROR",
    message="Validation error",
    status_code=400,
)

DATABASE_ERROR = AppError(
    code="DATABASE_ERROR",
    message="A database error occurred",
    status_code=500,
)

INVALID_DATE_FORMAT = AppError(
    code="INVALID_DATE_FORMAT",
    message="Date must be YYYY-MM-DD",
    status_code=400,
)

PARTICIPANTS_REQUIRED = AppError(
    code="PARTICIPANTS_REQUIRED",
    message="participant_ids must not be empty",
    status_code=400,
)

PARTICIPANTS_NOT_FOUND = AppError(
    code="PARTICIPANTS_NOT_FOUND",
    message="One or more participant_ids do not exist",
    status_code=400,
)

MISSING_INCOME = AppError(
    code="MISSING_INCOME",
    message="Missing income for income_ratio split",
    status_code=400,
)

INVALID_INCOME_TOTAL = AppError(
    code="INVALID_INCOME_TOTAL",
    message="Total average_income must be greater than 0",
    status_code=400,
)

ALLOCATION_ERROR = AppError(
    code="ALLOCATION_ERROR",
    message="Payment allocation error",
    status_code=400,
)