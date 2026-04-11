from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_income_ratio_route_fails_when_income_missing():
    client.post("/people", json={
        "name": "Cameron",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": None
    })
    client.post("/people", json={
        "name": "Wife",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 1500
    })

    person_resp = client.get("/people")
    first_person_id = person_resp.json()[0]["id"]

    account_resp = client.post("/accounts", json={
        "person_id": first_person_id,
        "name": "Bills Account",
        "account_type": "checking",
        "balance": 3000,
        "updated_at": "2026-04-10"
    })
    account_id = account_resp.json()["id"]

    response = client.post("/payments", json={
        "name": "Rent",
        "amount": 2000,
        "due_date": "2026-04-15",
        "category": "Housing",
        "account_id": account_id,
        "split_method": "income_ratio",
        "is_recurring": False,
        "due_day": None,
        "single_person_id": None
    })

    assert response.status_code == 400
    assert "missing average_income" in response.json()["detail"]