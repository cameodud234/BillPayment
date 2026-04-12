import pytest

from app.services import payments, people, accounts
from app.domain.person import PersonData
from app.domain.account import AccountData
from app.domain.payment import PaymentData, WeeklyBudgetData
from app.models.account_models import AccountType
from app.models.payment_models import PaymentCategory, SplitMethod


def test_create_payment(test_db):
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
            average_income=1000
        )
    )

    acct = accounts.create_account(
        AccountData(
            person_id=p1["id"],
            name="Bills Account",
            account_type=AccountType.checking,
            balance=3000,
            updated_at="2026-04-09"
        )
    )

    result = payments.create_payment(
        PaymentData(
            name="Internet",
            amount=100,
            due_date="2026-04-10",
            category=PaymentCategory.utilities,
            participant_ids=[p1["id"], p2["id"]],
            split_method=SplitMethod.equal,
            account_id=acct["id"],
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "ok"
    assert "id" in result


def test_weekly_budget(test_db):
    result = payments.get_weekly_budget(
        WeeklyBudgetData(payday="2026-04-07")
    )

    assert "total" in result
    assert "payments" in result


def test_recurring_payment_requires_due_day():
    with pytest.raises(ValueError, match="due_day is required for recurring payments"):
        PaymentData(
            name="Rent",
            amount=2800,
            due_date="2026-04-01",
            category=PaymentCategory.housing,
            participant_ids=[1],
            split_method=SplitMethod.equal,
            is_recurring=True,
            due_day=None
        )


def test_due_day_must_be_between_1_and_31():
    with pytest.raises(ValueError, match="due_day must be between 1 and 31"):
        PaymentData(
            name="Internet",
            amount=100,
            due_date="2026-04-15",
            category=PaymentCategory.utilities,
            participant_ids=[1],
            split_method=SplitMethod.equal,
            is_recurring=True,
            due_day=35
        )


def test_payment_amount_must_be_positive():
    with pytest.raises(ValueError, match="amount must be greater than 0"):
        PaymentData(
            name="Bad Payment",
            amount=0,
            due_date="2026-04-10",
            category=PaymentCategory.other,
            participant_ids=[1],
            split_method=SplitMethod.equal,
            is_recurring=False
        )


def test_participant_ids_must_not_be_empty():
    with pytest.raises(ValueError, match="participant_ids must not be empty"):
        PaymentData(
            name="No Participants",
            amount=50,
            due_date="2026-04-10",
            category=PaymentCategory.other,
            participant_ids=[],
            split_method=SplitMethod.equal,
            is_recurring=False
        )


def test_participant_ids_must_not_contain_duplicates():
    with pytest.raises(ValueError, match="participant_ids must not contain duplicates"):
        PaymentData(
            name="Duplicate Participants",
            amount=50,
            due_date="2026-04-10",
            category=PaymentCategory.other,
            participant_ids=[1, 1],
            split_method=SplitMethod.equal,
            is_recurring=False
        )