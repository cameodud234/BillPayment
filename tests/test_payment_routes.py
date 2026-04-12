from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def create_person(name: str, average_income: float | None = 1200):
    person_payload = {
        "name": name,
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": average_income
    }
    person_response = client.post("/people", json=person_payload)
    assert person_response.status_code == 200
    return person_response.json()["id"]


def create_account(person_id: int):
    account_payload = {
        "person_id": person_id,
        "name": "Payment Checking",
        "account_type": "checking",
        "balance": 3000,
        "updated_at": "2026-04-10"
    }
    account_response = client.post("/accounts", json=account_payload)
    assert account_response.status_code == 200
    return account_response.json()["id"]


def create_people_and_account():
    p1 = create_person("Payment Owner")
    p2 = create_person("Second Person")
    account_id = create_account(p1)
    return p1, p2, account_id


def test_get_payments_route():
    response = client.get("/payments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_payment_route_equal():
    p1, p2, account_id = create_people_and_account()

    payload = {
        "name": "Internet",
        "amount": 100,
        "due_date": "2026-04-15",
        "category": "Utilities",
        "account_id": account_id,
        "participant_ids": [p1, p2],
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "id" in body


def test_create_payment_route_single_person_as_equal():
    person_id = create_person("Solo Owner")
    account_id = create_account(person_id)

    payload = {
        "name": "Personal Subscription",
        "amount": 25,
        "due_date": "2026-04-16",
        "category": "Entertainment",
        "account_id": account_id,
        "participant_ids": [person_id],
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "id" in body


def test_create_payment_invalid_due_date():
    person_id = create_person("Bad Date Owner")
    account_id = create_account(person_id)

    payload = {
        "name": "Bad Date Payment",
        "amount": 50,
        "due_date": "04-15-2026",
        "category": "Other",
        "account_id": account_id,
        "participant_ids": [person_id],
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "due_date must be YYYY-MM-DD"


def test_create_payment_invalid_due_day():
    person_id = create_person("Bad Due Day Owner")
    account_id = create_account(person_id)

    payload = {
        "name": "Bad Due Day",
        "amount": 80,
        "due_date": "2026-04-15",
        "category": "Utilities",
        "account_id": account_id,
        "participant_ids": [person_id],
        "split_method": "equal",
        "is_recurring": True,
        "due_day": 40
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "due_day must be between 1 and 31"


def test_create_payment_empty_participants():
    person_id = create_person("Empty Participants Owner")
    account_id = create_account(person_id)

    payload = {
        "name": "No Participants Payment",
        "amount": 80,
        "due_date": "2026-04-15",
        "category": "Utilities",
        "account_id": account_id,
        "participant_ids": [],
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None
    }

    response = client.post("/payments", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "participant_ids must not be empty"


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