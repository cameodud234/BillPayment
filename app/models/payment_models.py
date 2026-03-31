from enum import Enum
from pydantic import BaseModel

class Category(str, Enum):
    names = "Names"
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
    category: Category