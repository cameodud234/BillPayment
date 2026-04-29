from dataclasses import dataclass


@dataclass(frozen=True)
class AppError:
    code: str
    message: str
    status_code: int


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