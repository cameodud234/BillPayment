from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import people

router = APIRouter()


class AddPersonRequest(BaseModel):
    name: str
    pay_schedule: str
    payday: str
    anchor_date: str | None = None
    average_income: float | None = None


@router.get("/people")
def get_people():
    return people.get_all_people()


@router.post("/people")
def add_person(data: AddPersonRequest):
    valid_schedules = {"weekly", "biweekly", "monthly"}

    if data.pay_schedule not in valid_schedules:
        raise HTTPException(
            status_code=400,
            detail=f"pay_schedule must be one of: {', '.join(valid_schedules)}"
        )

    valid_paydays = {
        "Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday"
    }

    if data.payday not in valid_paydays:
        raise HTTPException(
            status_code=400,
            detail="payday must be a valid weekday name"
        )

    if data.anchor_date:
        from datetime import datetime
        try:
            datetime.strptime(data.anchor_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="anchor_date must be YYYY-MM-DD")

    return people.create_person(
        name=data.name,
        pay_schedule=data.pay_schedule,
        payday=data.payday,
        anchor_date=data.anchor_date,
        average_income=data.average_income
    )