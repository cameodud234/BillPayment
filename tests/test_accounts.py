import sqlite3

import pytest
from app.services import accounts, people
from app.domain.account import AccountData
from app.domain.person import PersonData
from app.models.account_models import AccountType



def test_create_account(test_db):
    person = people.create_person(
        PersonData(
            name="Owner",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )

    result = accounts.create_account(
        AccountData(
            person_id=person["id"],
            name="Bills Checking",
            account_type=AccountType.checking,
            balance=2500,
            updated_at="2026-04-09"
        )
    )

    assert result["status"] == "ok"
    assert "id" in result


def test_get_total_balance(test_db):
    total = accounts.get_total_balance()
    assert isinstance(total, (int, float))


def test_update_account(test_db):
    person = people.create_person(
        PersonData(
            name="Acct Owner",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )

    created = accounts.create_account(
        AccountData(
            person_id=person["id"],
            name="Old Account",
            account_type=AccountType.checking,
            balance=100,
            updated_at="2026-04-09"
        )
    )

    result = accounts.update_account(
        created["id"],
        AccountData(
            person_id=person["id"],
            name="New Account",
            account_type=AccountType.savings,
            balance=500,
            updated_at="2026-04-10"
        )
    )

    assert result["status"] == "ok"


def test_delete_account(test_db):
    person = people.create_person(
        PersonData(
            name="Delete Owner",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )

    created = accounts.create_account(
        AccountData(
            person_id=person["id"],
            name="Delete Account",
            account_type=AccountType.checking,
            balance=200,
            updated_at="2026-04-09"
        )
    )

    result = accounts.delete_account(created["id"])
    assert result["status"] == "ok"


def test_account_balance_cannot_be_negative():
    with pytest.raises(ValueError, match="balance must be >= 0"):
        AccountData(
            person_id=2,
            name="Bad Account",
            account_type=AccountType.checking,
            balance=-5
        )

def test_account_cannot_add_multiple_accounts(test_db):
    person = people.create_person(
        PersonData(
            name="Cameron",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )
    person_id = person["id"]

    first = accounts.create_account(
        AccountData(
            person_id=person_id,
            name="Checking",
            account_type=AccountType.checking,
            balance=500
        )
    )
    assert first["status"] == "ok"

    second = accounts.create_account(
        AccountData(
            person_id=person_id,
            name="Savings",
            account_type=AccountType.savings,
            balance=300
        )
    )

    assert second["status"] == "error"
    assert second["message"] == "This person already has an account"

def test_account_can_be_created_for_person(test_db):
    person = people.create_person(
        PersonData(
            name="Owner",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )

    result = accounts.create_account(
        AccountData(
            person_id=person["id"],
            name="Checking",
            account_type=AccountType.checking,
            balance=100
        )
    )

    assert result["status"] == "ok"
    assert "id" in result

def test_different_people_can_each_have_one_account(test_db):
    p1 = people.create_person(
        PersonData(
            name="Cameron",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )
    p2 = people.create_person(
        PersonData(
            name="Wife",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1500
        )
    )

    a1 = accounts.create_account(
        AccountData(
            person_id=p1["id"],
            name="Cameron Checking",
            account_type=AccountType.checking,
            balance=100
        )
    )
    a2 = accounts.create_account(
        AccountData(
            person_id=p2["id"],
            name="Wife Checking",
            account_type=AccountType.checking,
            balance=200
        )
    )

    assert a1["status"] == "ok"
    assert a2["status"] == "ok"

def test_update_account_cannot_move_to_person_who_already_has_account(test_db):
    p1 = people.create_person(
        PersonData(
            name="Person One",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )
    p2 = people.create_person(
        PersonData(
            name="Person Two",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )

    a1 = accounts.create_account(
        AccountData(
            person_id=p1["id"],
            name="P1 Checking",
            account_type=AccountType.checking,
            balance=100
        )
    )
    a2 = accounts.create_account(
        AccountData(
            person_id=p2["id"],
            name="P2 Checking",
            account_type=AccountType.checking,
            balance=200
        )
    )

    result = accounts.update_account(
        a2["id"],
        AccountData(
            person_id=p1["id"],
            name="Moved Account",
            account_type=AccountType.checking,
            balance=200
        )
    )

    assert result["status"] == "error"

def test_get_total_balance_by_person_id_with_one_account(test_db):
    person = people.create_person(
        PersonData(
            name="Owner",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )

    accounts.create_account(
        AccountData(
            person_id=person["id"],
            name="Checking",
            account_type=AccountType.checking,
            balance=750
        )
    )

    result = accounts.get_total_balance_by_person_id(person["id"])

    assert result["status"] == "ok"
    assert result["person_id"] == person["id"]
    assert result["total_balance"] == 750


def test_delete_missing_account_returns_error(test_db):
    result = accounts.delete_account(999999)

    assert result["status"] == "error"
    assert result["message"] == "Account not found"

def test_get_total_balance_by_person_id(test_db):
    p1 = people.create_person(
        PersonData(
            name="Cameron",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )["id"]

    accounts.create_account(
        AccountData(
            person_id=p1,
            name="Checking",
            account_type=AccountType.checking,
            balance=1321,
            updated_at="2026-04-12"
        )
    )

    result = accounts.get_total_balance_by_person_id(p1)

    assert result["status"] == "ok"
    assert result["person_id"] == p1
    assert result["total_balance"] == 1321