from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def create_person(name: str, average_income: float | None = 1200):
    response = client.post("/people", json={
        "name": name,
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": average_income
    })
    assert response.status_code == 200
    return response.json()["id"]


def create_account(person_id: int):
    response = client.post("/accounts", json={
        "person_id": person_id,
        "name": "Bills Account",
        "account_type": "checking",
        "balance": 3000,
        "updated_at": "2026-04-10"
    })
    assert response.status_code == 200
    return response.json()["id"]


def test_get_payment_allocations_route(test_db):
    p1 = create_person("Cameron", 1000)
    p2 = create_person("Wife", 1500)
    account_id = create_account(p1)

    create_payment_response = client.post("/payments", json={
        "name": "Rent",
        "amount": 200,
        "due_date": "2026-04-15",
        "category": "Housing",
        "account_id": account_id,
        "participant_ids": [p1, p2],
        "split_method": "income_ratio",
        "is_recurring": False,
        "due_day": None
    })
    assert create_payment_response.status_code == 200
    payment_id = create_payment_response.json()["id"]

    response = client.get(f"/payments/{payment_id}/allocations")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["payment_id"] == payment_id
    assert len(body["allocations"]) == 2


def test_get_payment_allocations_route_not_found(test_db):
    response = client.get("/payments/999999/allocations")

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

def test_get_payment_allocations_route_returns_expected_values(test_db):
    p1 = create_person("Cameron", 1000)
    p2 = create_person("Wife", 1500)
    account_id = create_account(p1)

    create_payment_response = client.post("/payments", json={
        "name": "Rent",
        "amount": 200,
        "due_date": "2026-04-15",
        "category": "Housing",
        "account_id": account_id,
        "participant_ids": [p1, p2],
        "split_method": "income_ratio",
        "is_recurring": False,
        "due_day": None
    })
    assert create_payment_response.status_code == 200
    payment_id = create_payment_response.json()["id"]

    response = client.get(f"/payments/{payment_id}/allocations")
    assert response.status_code == 200

    allocations = response.json()["allocations"]
    by_person = {row["person_id"]: row for row in allocations}

    assert by_person[p1]["allocated_amount"] == 80.0
    assert by_person[p2]["allocated_amount"] == 120.0
    assert by_person[p1]["share_percentage"] == 40.0
    assert by_person[p2]["share_percentage"] == 60.0