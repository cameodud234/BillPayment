from dataclasses import dataclass
from typing import Optional
from app.models.account_models import AccountType

@dataclass
class AccountData:
    person_id: Optional[int]
    name: str
    account_type: AccountType
    balance: float = 0.0
    updated_at: Optional[str] = None

    def __post_init__(self):
        if self.balance < 0:
            raise ValueError("balance must be >= 0")