from enum import Enum
from pydantic import BaseModel


class PaymentCategory(str, Enum):
    housing = "Housing"
    utilities = "Utilities"
    groceries = "Groceries"
    transportation = "Transportation"
    entertainment = "Entertainment"
    technology = "Technology"
    education = "Education"
    business = "Business"
    other = "Other"


class AddPaymentRequest(BaseModel):
    name: str
    amount: float
    due_date: str
    category: PaymentCategory
    account_id: int | None = None
    is_recurring: int = 0
    due_day: int | None = None