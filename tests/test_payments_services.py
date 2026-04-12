import pytest

from app.services import payment_allocations, payments, people, accounts
from app.domain.person import PersonData
from app.domain.account import AccountData
from app.domain.payment import PaymentData, WeeklyBudgetData
from app.models.account_models import AccountType
from app.models.payment_models import PaymentCategory, SplitMethod


def create_service_person(name: str, income: float | None):
    return people.create_person(
        PersonData(
            name=name,
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=income
        )
    )["id"]


def create_service_account(person_id: int):
    return accounts.create_account(
        AccountData(
            person_id=person_id,
            name="Bills Account",
            account_type=AccountType.checking,
            balance=3000,
            updated_at="2026-04-10"
        )
    )["id"]


def test_create_payment(test_db):
    p1 = create_service_person("Cameron", 1000)
    p2 = create_service_person("Wife", 1000)
    account_id = create_service_account(p1)

    result = payments.create_payment(
        PaymentData(
            name="Internet",
            amount=100,
            due_date="2026-04-10",
            category=PaymentCategory.utilities,
            participant_ids=[p1, p2],
            split_method=SplitMethod.equal,
            account_id=account_id,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "ok"
    assert "id" in result


def test_update_payment_rebuilds_allocations(test_db):
    p1 = create_service_person("Cameron", 1000)
    p2 = create_service_person("Wife", 1500)
    account_id = create_service_account(p1)

    created = payments.create_payment(
        PaymentData(
            name="Rent",
            amount=200,
            due_date="2026-04-15",
            category=PaymentCategory.housing,
            account_id=account_id,
            participant_ids=[p1, p2],
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None
        )
    )

    assert created["status"] == "ok"
    payment_id = created["id"]

    before = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    before_by_person = payment_allocations.map_allocations_by_person_id(before)

    assert before_by_person[p1]["allocated_amount"] == 100.00
    assert before_by_person[p2]["allocated_amount"] == 100.00

    updated = payments.update_payment(
        payment_id,
        PaymentData(
            name="Rent Updated",
            amount=200,
            due_date="2026-04-20",
            category=PaymentCategory.housing,
            account_id=account_id,
            participant_ids=[p1, p2],
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None
        )
    )

    assert updated["status"] == "ok"
    assert updated["updated_id"] == payment_id

    after = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    after_by_person = payment_allocations.map_allocations_by_person_id(after)

    assert after_by_person[p1]["allocated_amount"] == 80.00
    assert after_by_person[p2]["allocated_amount"] == 120.00
    assert payment_allocations.sum_allocated_amounts(after) == 200.00


def test_update_payment_not_found(test_db):
    p1 = create_service_person("Cameron", 1000)

    result = payments.update_payment(
        999999,
        PaymentData(
            name="Missing Payment",
            amount=100,
            due_date="2026-04-15",
            category=PaymentCategory.other,
            account_id=None,
            participant_ids=[p1],
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "error"
    assert result["message"] == "Payment not found"


def test_delete_payment_removes_payment_and_allocations(test_db):
    p1 = create_service_person("Cameron", 1000)
    p2 = create_service_person("Wife", 1000)
    account_id = create_service_account(p1)

    created = payments.create_payment(
        PaymentData(
            name="Utilities",
            amount=120,
            due_date="2026-04-15",
            category=PaymentCategory.utilities,
            account_id=account_id,
            participant_ids=[p1, p2],
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None
        )
    )

    payment_id = created["id"]

    allocs_before = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    assert len(allocs_before) == 2

    deleted = payments.delete_payment(payment_id)
    assert deleted["status"] == "ok"
    assert deleted["deleted_id"] == payment_id

    assert payments.get_payment_by_id(payment_id) is None
    assert payment_allocations.fetch_allocations_by_payment_id(payment_id) == []


def test_delete_payment_not_found(test_db):
    result = payments.delete_payment(999999)

    assert result["status"] == "error"
    assert result["message"] == "Payment not found"


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