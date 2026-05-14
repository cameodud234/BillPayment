from app.services import people
from app.domain.person import PersonData
import pytest
from helpers import assert_service_error


def test_create_person(test_db):
    data = PersonData(
        name="Cameron",
        payday="Friday",
        pay_schedule="weekly",
        anchor_date=None,
        average_income=1000
    )

    result = people.create_person(data)

    assert result["status"] == "ok"
    assert "id" in result


def test_get_person_by_id(test_db):
    created = people.create_person(
        PersonData(
            name="Test Person",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=900
        )
    )

    person = people.get_person_by_id(created["id"])

    assert person is not None
    assert person["name"] == "Test Person"


def test_create_duplicate_person_returns_error(test_db):
    data = PersonData(
        name="Duplicate Person",
        payday="Friday",
        pay_schedule="weekly",
        anchor_date=None,
        average_income=1000
    )

    created = people.create_person(data)
    duplicate = people.create_person(data)

    assert created["status"] == "ok"
    assert_service_error(duplicate, "PERSON_ALREADY_EXISTS", "Person already exists", 409)


def test_update_person(test_db):
    created = people.create_person(
        PersonData(
            name="Old Name",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=800
        )
    )

    result = people.update_person(
        created["id"],
        PersonData(
            name="New Name",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1200
        )
    )

    assert result["status"] == "ok"

    updated = people.get_person_by_id(created["id"])
    assert updated["name"] == "New Name"
    assert updated["average_income"] == 1200


def test_delete_person(test_db):
    created = people.create_person(
        PersonData(
            name="Delete Me",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=700
        )
    )

    result = people.delete_person(created["id"])
    assert result["status"] == "ok"

    deleted = people.get_person_by_id(created["id"])
    assert deleted is None


def test_delete_missing_person_returns_error(test_db):
    result = people.delete_person(999999)

    assert_service_error(result, "PERSON_NOT_FOUND", "Person not found", 404)
