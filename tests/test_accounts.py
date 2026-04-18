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
            person_id=None,
            name="Bad Account",
            account_type=AccountType.checking,
            balance=-5
        )

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
            balance=1000,
            updated_at="2026-04-12"
        )
    )

    accounts.create_account(
        AccountData(
            person_id=p1,
            name="Savings",
            account_type=AccountType.savings,
            balance=2500,
            updated_at="2026-04-12"
        )
    )

    result = accounts.get_total_balance_by_person_id(p1)

    assert result["status"] == "ok"
    assert result["person_id"] == p1
    assert result["total_balance"] == 3500