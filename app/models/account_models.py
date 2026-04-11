from enum import Enum
from pydantic import BaseModel, Field


class AccountType(str, Enum):
    checking = "checking"
    savings = "savings"
    credit = "credit"
    cash = "cash"
    other = "other"


class AddAccountRequest(BaseModel):
    person_id: int | None = None
    name: str
    account_type: AccountType
    balance: float = Field(default=0, ge=0)
    updated_at: str | None = None

class UpdateAccountRequest(BaseModel):
    person_id: int | None = None
    name: str
    account_type: AccountType
    balance: float = Field(default=0, ge=0)
    updated_at: str | None = None