from pydantic import BaseModel, Field

class UpdatePersonRequest(BaseModel):
    name: str
    payday: str
    pay_schedule: str
    anchor_date: str | None = None
    average_income: float | None = Field(default=None, ge=0)

class AddPersonRequest(BaseModel):
    name: str
    payday: str
    pay_schedule: str
    anchor_date: str | None = None
    average_income: float | None = None