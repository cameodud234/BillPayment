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
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None,
            single_person_id=None
        )
    )

    assert result["status"] == "error"
    assert result["message"] == "Cannot use income_ratio split: no people exist."


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

    people.create_person(
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
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None,
            single_person_id=None
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

    people.create_person(
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
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None,
            single_person_id=None
        )
    )

    assert result["status"] == "error"
    assert result["message"] == "Cannot use income_ratio split: total average_income must be greater than 0."


def test_equal_fails_with_fewer_than_two_people(test_db):
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
            name="Internet",
            amount=100,
            due_date="2026-04-15",
            category=PaymentCategory.utilities,
            account_id=account_id,
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None,
            single_person_id=None
        )
    )

    assert result["status"] == "error"
    assert result["message"] == "Cannot use equal split: at least 2 people are required."


def test_single_fails_when_person_id_missing(test_db):
    with pytest.raises(ValueError, match="single_person_id is required when split_method is 'single'"):
        PaymentData(
            name="Personal Bill",
            amount=50,
            due_date="2026-04-15",
            category=PaymentCategory.other,
            account_id=None,
            split_method=SplitMethod.single,
            is_recurring=False,
            due_day=None,
            single_person_id=None
        )


def test_single_fails_when_person_id_does_not_exist(test_db):
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
            name="Personal Bill",
            amount=50,
            due_date="2026-04-15",
            category=PaymentCategory.other,
            account_id=account_id,
            split_method=SplitMethod.single,
            is_recurring=False,
            due_day=None,
            single_person_id=999999
        )
    )

    assert result["status"] == "error"
    assert result["message"] == "single_person_id does not exist."


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

    people.create_person(
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
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None,
            single_person_id=None
        )
    )

    assert result["status"] == "ok"
    assert "id" in result