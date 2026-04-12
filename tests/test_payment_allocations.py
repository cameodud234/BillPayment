from app.services import people, accounts, payments, payment_allocations
from app.domain.person import PersonData
from app.domain.account import AccountData
from app.domain.payment import PaymentData
from app.db.database import get_connection
from app.models.account_models import AccountType
from app.models.payment_models import PaymentCategory, SplitMethod


def create_person(name: str, income: float | None):
    return people.create_person(
        PersonData(
            name=name,
            payday="Friday",
            pay_schedule="weekly",
            anchor_date=None,
            average_income=income
        )
    )["id"]


def create_account(person_id: int):
    return accounts.create_account(
        AccountData(
            person_id=person_id,
            name="Bills Account",
            account_type=AccountType.checking,
            balance=3000,
            updated_at="2026-04-10"
        )
    )["id"]


def test_equal_split_creates_two_equal_allocations(test_db):
    p1 = create_person("Cameron", 1000)
    p2 = create_person("Wife", 1500)
    account_id = create_account(p1)

    result = payments.create_payment(
        PaymentData(
            name="Internet",
            amount=100,
            due_date="2026-04-15",
            category=PaymentCategory.utilities,
            account_id=account_id,
            participant_ids=[p1, p2],
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "ok"
    payment_id = result["id"]

    allocs = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    assert len(allocs) == 2

    by_person = payment_allocations.map_allocations_by_person_id(allocs)

    assert by_person[p1]["allocated_amount"] == 50.00
    assert by_person[p2]["allocated_amount"] == 50.00
    assert by_person[p1]["share_percentage"] == 50.0
    assert by_person[p2]["share_percentage"] == 50.0

    assert payment_allocations.sum_allocated_amounts(allocs) == 100.00
    assert payment_allocations.count_allocations_for_payment(payment_id) == 2


def test_income_ratio_split_creates_expected_allocations(test_db):
    p1 = create_person("Cameron", 1000)
    p2 = create_person("Wife", 1500)
    account_id = create_account(p1)

    result = payments.create_payment(
        PaymentData(
            name="Rent",
            amount=200,
            due_date="2026-04-15",
            category=PaymentCategory.housing,
            account_id=account_id,
            participant_ids=[p1, p2],
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "ok"
    payment_id = result["id"]

    allocs = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    assert len(allocs) == 2

    by_person = payment_allocations.map_allocations_by_person_id(allocs)

    # 1000 / 2500 = 40%
    # 1500 / 2500 = 60%
    assert by_person[p1]["allocated_amount"] == 80.00
    assert by_person[p2]["allocated_amount"] == 120.00
    assert by_person[p1]["share_percentage"] == 40.0
    assert by_person[p2]["share_percentage"] == 60.0

    assert payment_allocations.sum_allocated_amounts(allocs) == 200.00


def test_one_participant_gets_full_allocation(test_db):
    p1 = create_person("Cameron", 1000)
    account_id = create_account(p1)

    result = payments.create_payment(
        PaymentData(
            name="Personal Bill",
            amount=75,
            due_date="2026-04-15",
            category=PaymentCategory.other,
            account_id=account_id,
            participant_ids=[p1],
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "ok"
    payment_id = result["id"]

    allocs = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    assert len(allocs) == 1

    alloc = allocs[0]
    assert alloc["person_id"] == p1
    assert alloc["allocated_amount"] == 75.00
    assert alloc["share_percentage"] == 100.0


def test_equal_split_rounding_still_sums_to_total(test_db):
    p1 = create_person("A", 1000)
    p2 = create_person("B", 1000)
    p3 = create_person("C", 1000)
    account_id = create_account(p1)

    result = payments.create_payment(
        PaymentData(
            name="Odd Split",
            amount=100,
            due_date="2026-04-15",
            category=PaymentCategory.other,
            account_id=account_id,
            participant_ids=[p1, p2, p3],
            split_method=SplitMethod.equal,
            is_recurring=False,
            due_day=None
        )
    )

    assert result["status"] == "ok"
    payment_id = result["id"]

    allocs = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    assert len(allocs) == 3
    assert payment_allocations.sum_allocated_amounts(allocs) == 100.00


def test_delete_allocations_for_payment_removes_rows(test_db):
    p1 = create_person("Cameron", 1000)
    p2 = create_person("Wife", 1000)
    account_id = create_account(p1)

    result = payments.create_payment(
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

    assert result["status"] == "ok"
    payment_id = result["id"]

    before = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    assert len(before) == 2

    conn = get_connection()
    cursor = conn.cursor()
    try:
        payment_allocations.delete_allocations_for_payment(cursor, payment_id)
        conn.commit()
    finally:
        conn.close()

    after = payment_allocations.fetch_allocations_by_payment_id(payment_id)
    assert after == []
    assert payment_allocations.count_allocations_for_payment(payment_id) == 0


def test_get_payment_allocations_service_returns_allocations(test_db):
    p1 = create_person("Cameron", 1000)
    p2 = create_person("Wife", 1500)
    account_id = create_account(p1)

    created = payments.create_payment(
        PaymentData(
            name="Rent",
            amount=200,
            due_date="2026-04-15",
            category=PaymentCategory.housing,
            account_id=account_id,
            participant_ids=[p1, p2],
            split_method=SplitMethod.income_ratio,
            is_recurring=False,
            due_day=None
        )
    )

    assert created["status"] == "ok"
    payment_id = created["id"]

    result = payment_allocations.get_payment_allocations(payment_id)

    assert result["status"] == "ok"
    assert result["payment_id"] == payment_id
    assert len(result["allocations"]) == 2


def test_get_payment_allocations_service_not_found(test_db):
    result = payment_allocations.get_payment_allocations(999999)

    assert result["status"] == "error"
    assert result["message"] == "Payment not found"