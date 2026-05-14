from fastapi.testclient import TestClient
from main import app
from helpers import assert_route_error

client = TestClient(app)


def create_person(name: str, average_income: float | None = 1200):
    person_payload = {
        "name": name,
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": average_income
    }
    response = client.post("/people", json=person_payload)
    assert response.status_code == 200
    return response.json()["id"]


def create_account(
    person_id: int,
    name: str = "Bills Checking",
    account_type: str = "checking",
    balance: float = 2500,
    updated_at: str = "2026-04-10"
):
    account_payload = {
        "person_id": person_id,
        "name": name,
        "account_type": account_type,
        "balance": balance,
        "updated_at": updated_at
    }
    response = client.post("/accounts", json=account_payload)
    assert response.status_code == 200
    return response.json()["id"]


def test_get_accounts_route():
    response = client.get("/accounts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_missing_account_route_returns_structured_error(test_db):
    response = client.get("/accounts/999999")

    assert_route_error(response, 404, "ACCOUNT_NOT_FOUND", "Account not found")


def test_create_account_route():
    person_payload = {
        "name": "Account Owner",
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
        "name": "Bills Checking",
        "account_type": "checking",
        "balance": 2500,
        "updated_at": "2026-04-10"
    }

    response = client.post("/accounts", json=account_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "id" in body


def test_update_account_route():
    person_payload = {
        "name": "Update Owner",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 1000
    }
    person_response = client.post("/people", json=person_payload)
    person_id = person_response.json()["id"]

    create_payload = {
        "person_id": person_id,
        "name": "Old Account",
        "account_type": "checking",
        "balance": 100,
        "updated_at": "2026-04-10"
    }
    create_response = client.post("/accounts", json=create_payload)
    account_id = create_response.json()["id"]

    update_payload = {
        "person_id": person_id,
        "name": "New Account",
        "account_type": "savings",
        "balance": 500,
        "updated_at": "2026-04-11"
    }

    response = client.put(f"/accounts/{account_id}", json=update_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["updated_id"] == account_id


def test_delete_account_route():
    person_payload = {
        "name": "Delete Owner",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 1000
    }
    person_response = client.post("/people", json=person_payload)
    person_id = person_response.json()["id"]

    create_payload = {
        "person_id": person_id,
        "name": "Delete Me",
        "account_type": "checking",
        "balance": 200,
        "updated_at": "2026-04-10"
    }
    create_response = client.post("/accounts", json=create_payload)
    account_id = create_response.json()["id"]

    response = client.delete(f"/accounts/{account_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["deleted_id"] == account_id

def test_get_total_balance_for_person_route(test_db):
    p1 = create_person("Cameron", 1000)
    create_account(p1)
    client.post("/accounts", json={
        "person_id": p1,
        "name": "Savings",
        "account_type": "savings",
        "balance": 2000,
        "updated_at": "2026-04-12"
    })

    response = client.get(f"/people/{p1}/accounts/total")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["person_id"] == p1

def test_create_second_account_for_same_person_route_fails(test_db):
    person_resp = client.post("/people", json={
        "name": "Owner",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 1000
    })
    person_id = person_resp.json()["id"]

    first = client.post("/accounts", json={
        "person_id": person_id,
        "name": "Checking",
        "account_type": "checking",
        "balance": 100,
        "updated_at": "2026-04-12"
    })
    assert first.status_code == 200

    second = client.post("/accounts", json={
        "person_id": person_id,
        "name": "Savings",
        "account_type": "savings",
        "balance": 200,
        "updated_at": "2026-04-12"
    })

    assert_route_error(
        second,
        409,
        "PERSON_ACCOUNT_EXISTS",
        "This person already has an account"
    )


def test_create_account_for_missing_person_route_fails(test_db):
    response = client.post("/accounts", json={
        "person_id": 999999,
        "name": "Ghost Checking",
        "account_type": "checking",
        "balance": 100,
        "updated_at": "2026-04-12"
    })

    assert_route_error(response, 404, "PERSON_NOT_FOUND", "Person not found")
