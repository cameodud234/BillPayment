from dataclasses import dataclass
from typing import Optional

@dataclass
class PersonData:
    name: str
    payday: str
    pay_schedule: str
    anchor_date: Optional[str] = None
    average_income: Optional[float] = None

    def __post_init__(self):
        if self.average_income is not None and self.average_income < 0:
            raise ValueError("average_income must be >= 0")