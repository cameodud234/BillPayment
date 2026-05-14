from datetime import datetime
from fastapi import APIRouter

from app.services import people
from app.models import person_models
from app.domain.person import PersonData
from app.config import VALID_PAYDAYS, VALID_SCHEDULES
from app import errors

router = APIRouter()


@router.get("/people")
def get_people():
    return people.get_all_people()


@router.get("/people/{person_id}")
def get_person(person_id: int):
    person = people.get_person_by_id(person_id)

    if person is None:
        errors.raise_http_error(errors.PERSON_NOT_FOUND)

    return person


@router.post("/people")
def add_person(data: person_models.AddPersonRequest):

    if data.pay_schedule not in VALID_SCHEDULES:
        errors.raise_http_error(
            errors.VALIDATION_ERROR,
            f"pay_schedule must be one of: {', '.join(VALID_SCHEDULES)}"
        )

    if data.payday not in VALID_PAYDAYS:
        errors.raise_http_error(errors.VALIDATION_ERROR, "payday must be a valid weekday name")

    if data.anchor_date:
        try:
            datetime.strptime(data.anchor_date, "%Y-%m-%d")
        except ValueError:
            errors.raise_http_error(errors.VALIDATION_ERROR, "anchor_date must be YYYY-MM-DD")

    try:
        person = PersonData(**data.model_dump())
    except ValueError as e:
        errors.raise_http_error(errors.VALIDATION_ERROR, str(e))

    result = people.create_person(person)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result


@router.put("/people/{person_id}")
def update_person(person_id: int, data: person_models.UpdatePersonRequest):
    if data.pay_schedule not in VALID_SCHEDULES:
        errors.raise_http_error(
            errors.VALIDATION_ERROR,
            f"pay_schedule must be one of: {', '.join(VALID_SCHEDULES)}"
        )

    if data.payday not in VALID_PAYDAYS:
        errors.raise_http_error(errors.VALIDATION_ERROR, "payday must be a valid weekday name")

    if data.anchor_date:
        try:
            datetime.strptime(data.anchor_date, "%Y-%m-%d")
        except ValueError:
            errors.raise_http_error(errors.VALIDATION_ERROR, "anchor_date must be YYYY-MM-DD")

    try:
        person = PersonData(**data.model_dump())
    except ValueError as e:
        errors.raise_http_error(errors.VALIDATION_ERROR, str(e))

    result = people.update_person(person_id, person)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result


@router.delete("/people/{person_id}")
def delete_person(person_id: int):
    result = people.delete_person(person_id)

    if result["status"] == "error":
        errors.raise_result_error(result)

    return result
