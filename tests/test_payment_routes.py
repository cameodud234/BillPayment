from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def create_person_and_account():
    person_payload = {
        "name": "Payment Owner",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 1200
    }
    person_response = client.post("/people", json=person_payload)
    assert person_response.status_code == 200
    person_id = person_response.json()["id"]

    account_payload = {
        "person_id": person_id,
        "name": "Payment Checking",
        "account_type": "checking",
        "balance": 3000,
        "updated_at": "2026-04-10"
    }
    account_response = client.post("/accounts", json=account_payload)
    assert account_response.status_code == 200
    account_id = account_response.json()["id"]

    return person_id, account_id


def test_get_payments_route():
    response = client.get("/payments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_payment_route_equal():
    _, account_id = create_person_and_account()

    payload = {
        "name": "Internet",
        "amount": 100,
        "due_date": "2026-04-15",
        "category": "Utilities",
        "account_id": account_id,
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None,
        "single_person_id": None
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "id" in body


def test_create_payment_route_single():
    person_id, account_id = create_person_and_account()

    payload = {
        "name": "Personal Subscription",
        "amount": 25,
        "due_date": "2026-04-16",
        "category": "Entertainment",
        "account_id": account_id,
        "split_method": "single",
        "is_recurring": False,
        "due_day": None,
        "single_person_id": person_id
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "id" in body


def test_create_payment_invalid_due_date():
    _, account_id = create_person_and_account()

    payload = {
        "name": "Bad Date Payment",
        "amount": 50,
        "due_date": "04-15-2026",
        "category": "Other",
        "account_id": account_id,
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None,
        "single_person_id": None
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "due_date must be YYYY-MM-DD"


def test_create_payment_invalid_due_day():
    _, account_id = create_person_and_account()

    payload = {
        "name": "Bad Due Day",
        "amount": 80,
        "due_date": "2026-04-15",
        "category": "Utilities",
        "account_id": account_id,
        "split_method": "equal",
        "is_recurring": True,
        "due_day": 40,
        "single_person_id": None
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "due_day must be between 1 and 31"


def test_weekly_budget_route():
    response = client.post("/payments/weekly", json={"payday": "2026-04-07"})

    assert response.status_code == 200
    body = response.json()
    assert "total" in body
    assert "payments" in body


def test_weekly_budget_invalid_date():
    response = client.post("/payments/weekly", json={"payday": "04/07/2026"})

    assert response.status_code == 400
    assert response.json()["detail"] == "payday must be YYYY-MM-DD"