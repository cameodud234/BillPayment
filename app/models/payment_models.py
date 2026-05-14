from enum import Enum
from pydantic import BaseModel, Field


class WeeklyBudgetRequest(BaseModel):
    payday: str


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


class SplitMethod(str, Enum):
    equal = "equal"
    income_ratio = "income_ratio"


class AddPaymentRequest(BaseModel):
    name: str
    amount: float = Field(gt=0)
    due_date: str
    category: PaymentCategory
    account_id: int | None = None
    participant_ids: list[int]
    split_method: SplitMethod
    is_recurring: bool = False
    due_day: int | None = None