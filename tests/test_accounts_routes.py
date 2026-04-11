from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_accounts_route():
    response = client.get("/accounts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_account_route():
    # first create a person so we have a valid person_id
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