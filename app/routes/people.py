from fastapi import APIRouter, HTTPException
from app.services import people
from app.models import person_models
from app.config import VALID_PAYDAYS, VALID_SCHEDULES

router = APIRouter()

@router.get("/people")
def get_people():
    return people.get_all_people()


@router.post("/people")
def add_person(data: person_models.AddPersonRequest):

    if data.pay_schedule not in VALID_SCHEDULES:
        raise HTTPException(
            status_code=400,
            detail=f"pay_schedule must be one of: {', '.join(VALID_SCHEDULES)}"
        )

    if data.payday not in VALID_PAYDAYS:
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
        
    return people.create_person(data)


@router.put("/people/{person_id}")
def update_person(person_id: int, data: person_models.UpdatePersonRequest):
    result = people.update_person(person_id, data)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return result