import pytest

from app.services import payments, people, accounts
from app.domain.person import PersonData
from app.domain.account import AccountData
from app.domain.payment import PaymentData
from app.models.account_models import AccountType
from app.models.payment_models import PaymentCategory, SplitMethod


def create_account_for_tests(person_id: int):
    acct = accounts.create_account(
        AccountData(
            person_id=person_id,
            name="Bills Account",
            account_type=AccountType.checking,
            balance=3000,
            updated_at="2026-04-10"
        )
    )
    return acct["id"]


def test_income_ratio_fails_when_no_people_exist(test_db):
    result = payments.create_payment(
        PaymentData(
            name="Rent",
            amount=1000,
            due_date="2026-04-15",
            category=PaymentCategory.housing,
            account_id=None,
            participant_ids=[1],
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "error"
    assert result["message"] == "One or more participant_ids do not exist."


def test_income_ratio_fails_when_income_missing(test_db):
    p1 = people.create_person(
        PersonData(
            name="Cameron",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=None
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

    account_id = create_account_for_tests(p1["id"])

    result = payments.create_payment(
        PaymentData(
            name="Rent",
            amount=2000,
            due_date="2026-04-15",
            category=PaymentCategory.housing,
            account_id=account_id,
            participant_ids=[p1["id"], p2["id"]],
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "error"
    assert "missing average_income" in result["message"]
    assert "Cameron" in result["message"]


def test_income_ratio_fails_when_total_income_is_zero(test_db):
    p1 = people.create_person(
        PersonData(
            name="Cameron",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=0
        )
    )

    p2 = people.create_person(
        PersonData(
            name="Wife",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=0
        )
    )

    account_id = create_account_for_tests(p1["id"])

    result = payments.create_payment(
        PaymentData(
            name="Rent",
            amount=2000,
            due_date="2026-04-15",
            category=PaymentCategory.housing,
            account_id=account_id,
            participant_ids=[p1["id"], p2["id"]],
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "error"
    assert result["message"] == "Cannot use income_ratio split: total average_income must be greater than 0."


def test_equal_with_one_participant_succeeds(test_db):
    p1 = people.create_person(
        PersonData(
            name="Only Person",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )

    account_id = create_account_for_tests(p1["id"])

    result = payments.create_payment(
        PaymentData(
            name="Personal Internet",
            amount=100,
            due_date="2026-04-15",
            category=PaymentCategory.utilities,
            account_id=account_id,
            participant_ids=[p1["id"]],
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "ok"
    assert "id" in result


def test_equal_fails_when_participant_id_does_not_exist(test_db):
    p1 = people.create_person(
        PersonData(
            name="Owner",
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=1000
        )
    )

    account_id = create_account_for_tests(p1["id"])

    result = payments.create_payment(
        PaymentData(
            name="Utilities",
            amount=100,
            due_date="2026-04-15",
            category=PaymentCategory.utilities,
            account_id=account_id,
            participant_ids=[p1["id"], 999999],
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "error"
    assert result["message"] == "One or more participant_ids do not exist."


def test_income_ratio_succeeds_with_valid_income_data(test_db):
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

    account_id = create_account_for_tests(p1["id"])

    result = payments.create_payment(
        PaymentData(
            name="Rent",
            amount=2500,
            due_date="2026-04-15",
            category=PaymentCategory.housing,
            account_id=account_id,
            participant_ids=[p1["id"], p2["id"]],
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "ok"
    assert "id" in result