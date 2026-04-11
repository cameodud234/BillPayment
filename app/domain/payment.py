from dataclasses import dataclass
from typing import Optional
from app.models.payment_models import PaymentCategory, SplitMethod


@dataclass
class WeeklyBudgetData:
    payday: str


@dataclass
class PaymentData:
    name: str
    amount: float
    due_date: str
    category: PaymentCategory
    account_id: Optional[int] = None
    split_method: SplitMethod = SplitMethod.equal
    is_recurring: int = 0
    due_day: Optional[int] = None

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("amount must be greater than 0")

        if self.is_recurring and self.due_day is None:
            raise ValueError("due_day is required for recurring payments")

        if self.due_day is not None:
            if not (1 <= self.due_day <= 31):
                raise ValueError("due_day must be between 1 and 31")