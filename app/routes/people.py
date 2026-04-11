from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.services import people
from app.models import person_models
from app.domain.person import PersonData
from app.config import VALID_PAYDAYS, VALID_SCHEDULES

router = APIRouter()


@router.get("/people")
def get_people():
    return people.get_all_people()


@router.get("/people/{person_id}")
def get_person(person_id: int):
    person = people.get_person_by_id(person_id)

    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    return person


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
        try:
            datetime.strptime(data.anchor_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="anchor_date must be YYYY-MM-DD")

    try:
        person = PersonData(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return people.create_person(person)


@router.put("/people/{person_id}")
def update_person(person_id: int, data: person_models.UpdatePersonRequest):
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
        try:
            datetime.strptime(data.anchor_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="anchor_date must be YYYY-MM-DD")

    try:
        person = PersonData(**data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    result = people.update_person(person_id, person)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return result


@router.delete("/people/{person_id}")
def delete_person(person_id: int):
    result = people.delete_person(person_id)

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])

    return result