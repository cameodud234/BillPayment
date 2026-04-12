from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_income_ratio_route_fails_when_income_missing():
    create_cameron = client.post("/people", json={
        "name": "Cameron",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": None
    })
    assert create_cameron.status_code == 200
    cameron_id = create_cameron.json()["id"]

    create_wife = client.post("/people", json={
        "name": "Wife",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 1500
    })
    assert create_wife.status_code == 200
    wife_id = create_wife.json()["id"]

    account_resp = client.post("/accounts", json={
        "person_id": cameron_id,
        "name": "Bills Account",
        "account_type": "checking",
        "balance": 3000,
        "updated_at": "2026-04-10"
    })
    assert account_resp.status_code == 200
    account_id = account_resp.json()["id"]

    response = client.post("/payments", json={
        "name": "Rent",
        "amount": 2000,
        "due_date": "2026-04-15",
        "category": "Housing",
        "account_id": account_id,
        "participant_ids": [cameron_id, wife_id],
        "split_method": "income_ratio",
        "is_recurring": False,
        "due_day": None
    })

    assert response.status_code == 400
    assert "missing average_income" in response.json()["detail"]