from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_people_route():
    response = client.get("/people")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_person_by_id_route():
    payload = {
        "name": "Lookup Person",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 1000
    }
    create_response = client.post("/people", json=payload)
    person_id = create_response.json()["id"]

    response = client.get(f"/people/{person_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == person_id
    assert body["name"] == "Lookup Person"


def test_update_person_route():
    payload = {
        "name": "Old Person",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 900
    }
    create_response = client.post("/people", json=payload)
    person_id = create_response.json()["id"]

    update_payload = {
        "name": "New Person",
        "payday": "Friday",
        "pay_schedule": "biweekly",
        "anchor_date": "2026-03-20",
        "average_income": 1400
    }

    response = client.put(f"/people/{person_id}", json=update_payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["updated_id"] == person_id


def test_delete_person_route():
    payload = {
        "name": "Delete Person",
        "payday": "Friday",
        "pay_schedule": "weekly",
        "anchor_date": None,
        "average_income": 700
    }
    create_response = client.post("/people", json=payload)
    person_id = create_response.json()["id"]

    response = client.delete(f"/people/{person_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["deleted_id"] == person_id

def test_get_missing_person():
    response = client.get("/people/999999")
    assert response.status_code == 404