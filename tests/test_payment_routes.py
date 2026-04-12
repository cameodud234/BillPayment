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

def create_payment(account_id: int, participant_ids: list[int]):
    payment_payload = {
        "name": "Internet",
        "amount": 100,
        "due_date": "2026-04-15",
        "category": "Utilities",
        "account_id": account_id,
        "participant_ids": participant_ids,
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None
    }

    payment_response = client.post("/payments", json=payment_payload)
    assert payment_response.status_code == 200
    return payment_response.json()["id"]

def test_update_payment_route():
    p1 = create_person("Cameron", 1000)
    p2 = create_person("Wife", 1500)
    account_id = create_account(p1)

    create_payload = {
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

    create_response = client.post("/payments", json=create_payload)
    assert create_response.status_code == 200
    payment_id = create_response.json()["id"]

    update_payload = {
        "name": "Internet Updated",
        "amount": 120,
        "due_date": "2026-04-20",
        "category": "Utilities",
        "account_id": account_id,
        "participant_ids": [p1, p2],
        "split_method": "income_ratio",
        "is_recurring": False,
        "due_day": None
    }

    response = client.put(f"/payments/{payment_id}", json=update_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["updated_id"] == payment_id


def test_update_payment_route_not_found():
    p1 = create_person("Ghost Owner", 1000)

    payload = {
        "name": "Missing Payment",
        "amount": 100,
        "due_date": "2026-04-15",
        "category": "Other",
        "account_id": None,
        "participant_ids": [p1],
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None
    }

    response = client.put("/payments/999999", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"


def test_delete_payment_route():
    p1 = create_person("Delete Owner", 1000)
    account_id = create_account(p1)

    create_payload = {
        "name": "Delete Me",
        "amount": 50,
        "due_date": "2026-04-15",
        "category": "Other",
        "account_id": account_id,
        "participant_ids": [p1],
        "split_method": "equal",
        "is_recurring": False,
        "due_day": None
    }

    create_response = client.post("/payments", json=create_payload)
    assert create_response.status_code == 200
    payment_id = create_response.json()["id"]

    response = client.delete(f"/payments/{payment_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["deleted_id"] == payment_id


def test_delete_payment_route_not_found():
    response = client.delete("/payments/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

def test_delete_payment_route_again(test_db):
        
    p1 = create_person("Delete Owner", 1000)
    account_id = create_account(p1)
    payment_id = create_payment(account_id, [p1])

    response = client.delete(f"/payments/{payment_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["deleted_id"] == payment_id


def test_delete_payment_route_removes_allocations(test_db):
    p1 = create_person("Delete Owner", 1000)
    p2 = create_person("Second", 1000)
    account_id = create_account(p1)
    payment_id = create_payment(account_id, [p1, p2])

    delete_response = client.delete(f"/payments/{payment_id}")
    assert delete_response.status_code == 200

    alloc_response = client.get(f"/payments/{payment_id}/allocations")
    assert alloc_response.status_code == 404
    assert alloc_response.json()["detail"] == "Payment not found"